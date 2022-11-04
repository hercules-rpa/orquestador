from SPARQLWrapper import SPARQLWrapper, JSON
import pandas as pd
from model.process.Process2.Entities.Patent import Patent
from model.process.Process2.Entities.Conference import Conference
from model.process.Process2.Entities.ResearcherData import ResearcherData
from model.process.Process2.Entities.Enums.ResearcherIdentifyType import ResearcherIdentifyType
from model.process.Process2.Entities.RO import RO

class EDMA():
    def __init__(self, host:str='', port:str=''):
        self.host = host
        self.port = port
        if self.host and self.port:
            self.endpoint_sparql = self.host + ":" + self.port + "/sparql"
            self.sparql = SPARQLWrapper(self.endpoint_sparql)
            self.sparql.setReturnFormat(JSON)

    def get_all_articles(self, start_date: str, end_date: str):
        """
        Método para obtener la lista de artículos filtrada por un rango de fechas
        :param start_date fecha de inicio
        :param end_date fecha de fin
        :return DataFrame objeto respuesta
        """
        filter = "FILTER(?aniomesdia>=" + start_date + " AND ?aniomesdia<=" + end_date + ")"
        self.sparql.setQuery(
            """
            select ?s ?nombreDoc ?nombreRevista ?aniomesdia ?fecha group_concat(?nombreArea;separator="|") as ?nombreArea ?autor ?ORCID from <http://gnoss.com/b836078b-78a0-4939-b809-3f2ccf4e5c01>
            where
            {
                ?s a 'document'.

                ?s <http://w3id.org/roh/title> ?nombreDoc.

                ?s <http://purl.org/dc/terms/issued> ?fecha.

                BIND(?fecha/1000000 as ?aniomesdia).

                ?s <http://purl.org/ontology/bibo/authorList> ?authorList.

                OPTIONAL{

                   ?s <http://vivoweb.org/ontology/core#hasPublicationVenue> ?revista.

                  ?revista <http://w3id.org/roh/title> ?nombreRevista.

                }

                ?authorList <http://www.w3.org/1999/02/22-rdf-syntax-ns#member> ?persona.

                ?persona <http://xmlns.com/foaf/0.1/name> ?autor.

                OPTIONAL{

                  ?persona <http://w3id.org/roh/ORCID> ?ORCID

                }
                OPTIONAL{

                               ?s <http://w3id.org/roh/hasKnowledgeArea> ?area.

                               ?area <http://w3id.org/roh/categoryNode> ?nodo.

                               ?nodo <http://www.w3.org/2008/05/skos#prefLabel> ?nombreArea.

                               MINUS{?nodo <http://www.w3.org/2008/05/skos#narrower> ?hijos}

                }

                 """+ filter +"""
            }order by desc(?fecha) desc(?s)
            """
        )

        try:
            ret = self.sparql.queryAndConvert()
            df = pd.json_normalize(ret["results"]["bindings"])
            return df
        except Exception as e:
            print(e)
            print('ERROR en la obtención de artículos')
        return pd.DataFrame()

    def get_tecnology_offers(self, start_date: str, end_date: str):
        """
        Método para obtener la lista de oferta tecnológica filtrada por un rango de fechas
        :param start_date fecha de inicio
        :param end_date fecha de fin
        :return DataFrame objeto respuesta
        """
        filter = "FILTER(?fecha>="+start_date+" && ?fecha <=" +end_date+")"
        self.sparql.setQuery(
            """
            select * from <http://gnoss.com/b836078b-78a0-4939-b809-3f2ccf4e5c01> where {
            ?idOferta a 'offer'.
            ?idOferta  <http://www.schema.org/name> ?titulo.
            ?idOferta  <http://www.schema.org/description> ?description.
            ?idOferta  <http://www.schema.org/availability> <http://gnoss.com/items/offerstate_003>.
            ?idOferta  <http://w3id.org/roh/researchers> ?investigador.
            ?investigador foaf:name ?nombre.
            ?idOferta   <http://purl.org/dc/terms/issued> ?fecha
            """+ filter +"""
            }order by desc(?fecha) desc(?s)
            """)

        try:
            ret = self.sparql.queryAndConvert()
            df = pd.json_normalize(ret["results"]["bindings"])
            return df
        except Exception as e:
            print(e)
            print('ERROR en la obtención de oferta tecnológica')
        return pd.DataFrame()

    def get_researcher_data(self, researcherInfo) -> ResearcherData:
        """
        Método que obtiene los datos del investigador en base a un tipo de identificador y a un id.
        :param researcherInfo tupla con el tipo de identificador y el identificador del investigador
        :return ResearcherData objeto que contiene los datos del investigador
        """
        filter = self.get_researcher_filters(researcherInfo)
        if filter:
            self.sparql.setQuery(
                """
            select ?person ?nombreCompleto ?email ?nombreDepartamento ?nombreUniversidad from <http://gnoss.com/b836078b-78a0-4939-b809-3f2ccf4e5c01>
            where 
            {
                ?person a 'person'.
                ?person <http://xmlns.com/foaf/0.1/name> ?nombreCompleto.
                OPTIONAL{
                    ?person <http://vivoweb.org/ontology/core#departmentOrSchool> ?departamento.
                    ?departamento <http://purl.org/dc/elements/1.1/title> ?nombreDepartamento.
                }
                OPTIONAL{
                    ?person <http://w3id.org/roh/hasRole> ?org.
                    ?org <http://w3id.org/roh/title> ?nombreUniversidad .
                }
                OPTIONAL{
            ?person <https://www.w3.org/2006/vcard/ns#email> ?email.
            }
            """ + filter + """                
            }
            """
            )

            try:
                ret = self.sparql.queryAndConvert()
                df = pd.json_normalize(ret["results"]["bindings"])
                if not df.empty:
                    researcher_data = ResearcherData()
                    researcher_data.set_properties(df)
                    return researcher_data
            except Exception as e:
                print(e)
                print('ERROR al tratar los parámetros de los datos del investigador')
        else:
            print(
                'ERROR al obtener el filter de búsqueda para filtrar por identificador.')
        return None

    def get_chapters_books(self, researcherInfo, period):
        """
        Método qude obtiene los capítulos de libros de un investigador en base a un período de años.
        :param researcherInfo tupla con el tipo de identificador y el identificador del investigador
        :param period cadena de años separada por comas que indica el período para realizar la búsqueda
        :return DataFrame objeto respuesta
        """
        filter = self.get_researcher_filters(researcherInfo)
        filter_periodo = ''
        if period:
            filter_periodo = """FILTER(?anioFecha in ("""+period+"""))"""
        if filter:
            self.sparql.setQuery(
                """
            select ?doc ?titulo ?anioFecha ?tipoProduccion from <http://gnoss.com/b836078b-78a0-4939-b809-3f2ccf4e5c01>
            where
            {
                            ?doc a 'document'.
                            ?doc <http://w3id.org/roh/title> ?titulo .
                            ?doc <http://purl.org/dc/elements/1.1/type> ?typeProduccion.
                            ?typeProduccion <http://purl.org/dc/elements/1.1/title> ?tipoProduccion .
                            FILTER(lang(?tipoProduccion)='es')
                            ?doc <http://w3id.org/roh/isValidated> 'true'.
                            ?doc <http://purl.org/ontology/bibo/authorList> ?listAuthor.
                            ?doc <http://purl.org/dc/terms/issued> ?fecha. 
                            BIND(?fecha/10000000000 as ?anioFecha).
                            ?listAuthor <http://www.w3.org/1999/02/22-rdf-syntax-ns#member> ?person.

                            """+filter+filter_periodo+"""
                            FILTER(?typeProduccion=<http://gnoss.com/items/publicationtype_004>)
            }
                    """
            )

            try:
                ret = self.sparql.queryAndConvert()
                df = pd.json_normalize(ret["results"]["bindings"])
                return df

            except Exception as e:
                print(e)
                print('ERROR al obtener los capítulos de libros.')

        else:
            print(
                'ERROR al obtener el filter de búsqueda para filtrar por identificador.')
        return pd.DataFrame()

    def get_researcher_filters(self, researcherInfo: tuple) -> str:
        """
        Método encargado de obtener el filter de un investigador en base al tipo de identificador y al identificador.
        :param researcherInfo tupla con el tipo de identificador y el identificador del investigador
        :return str cadena con el filtro
        """
        if researcherInfo:
            if researcherInfo[0] == ResearcherIdentifyType.PERSONAREF:
                return """?person <http://w3id.org/roh/crisIdentifier> ?identifier.
                        FILTER(?identifier='"""+researcherInfo[1]+"""')"""

            if researcherInfo[0] == ResearcherIdentifyType.ORCID:
                return """?person <http://w3id.org/roh/ORCID> ?orcid.
                        FILTER(?orcid='"""+researcherInfo[1]+"""') """

            if researcherInfo[0] == ResearcherIdentifyType.EMAIL:
                return """?person <https://www.w3.org/2006/vcard/ns#email> ?email.
                        FILTER(?email='"""+researcherInfo[1]+"""')"""

        return None

    def get_books(self, researcherInfo, period):
        """
        Método encargado de obtener los libros de un investigador en base a un período.
        :param researcherInfo tupla con el tipo de identificador y el identificador del investigador
        :param period cadena de años separada por comas que indica el período para realizar la búsqueda
        :return DataFrame objeto respuesta
        """
        filter = self.get_researcher_filters(researcherInfo)
        filter_periodo = ''
        if period:
            filter_periodo = """FILTER(?anioFecha in ("""+period+"""))"""
        if filter:
            self.sparql.setQuery(
                """
            select ?doc ?titulo ?anioFecha ?tipoProduccion from <http://gnoss.com/b836078b-78a0-4939-b809-3f2ccf4e5c01>
            where
            {
                            ?doc a 'document'.
                            ?doc <http://w3id.org/roh/title> ?titulo .
                            ?doc <http://purl.org/dc/elements/1.1/type> ?typeProduccion.
                            ?typeProduccion <http://purl.org/dc/elements/1.1/title> ?tipoProduccion .
                            FILTER(lang(?tipoProduccion)='es')
                            ?doc <http://w3id.org/roh/isValidated> 'true'.
                            ?doc <http://purl.org/ontology/bibo/authorList> ?listAuthor.
                            ?doc <http://purl.org/dc/terms/issued> ?fecha. 
                            BIND(?fecha/10000000000 as ?anioFecha).
                            ?listAuthor <http://www.w3.org/1999/02/22-rdf-syntax-ns#member> ?person.

                            """+filter+filter_periodo+"""
                            FILTER(?typeProduccion=<http://gnoss.com/items/publicationtype_032>)
            }
                    """
            )

            try:
                ret = self.sparql.queryAndConvert()
                df = pd.json_normalize(ret["results"]["bindings"])
                return df

            except Exception as e:
                print(e)
                print('ERROR al obtener la lista de libros')

        else:
            print('ERROR al obtener el filter de búsqueda para filtrar por identificador.')
        return pd.DataFrame()

    
    def get_researcher_articles(self,researcherInfo, max_article:int, period, authorship_order):
        """
        Método que obtiene la lista de artículos de un investigador.
        :param researcherInfo tupla con el tipo de identificador y el identificador del investigador
        :param max_article número máximo de artículos que se deben obtener
        :param period cadena de años separada por comas que indica el período para realizar la búsqueda
        :param authorship_order indica si es necesario ordenar por autoría
        :return DataFrame objeto respuesta
        """
        filter = self.get_researcher_filters(researcherInfo)
        filter_periodo = ''
        if period:
            filter_periodo = """FILTER(?anioFecha in ("""+period+"""))"""
        if filter:
            self.sparql.setQuery(
            """
            select distinct ?doc ?citasWos ?citasScopus ?citasSemanticScholar ?tipoProduccion ?title ?posicion ?autorUnico ?quartile from <http://gnoss.com/b836078b-78a0-4939-b809-3f2ccf4e5c01>
            where 
            {
                            select distinct ?title ?citasWos ?citasScopus ?citasSemanticScholar ?tipoProduccion ?posicion ?doc min(?quartile) as ?quartile ?nombreFuenteIndiceImpacto !(max(?dif)) as ?autorUnico
                            where
                            {
                                ?doc a 'document'.
                                ?doc <http://w3id.org/roh/title> ?title.
                                ?doc <http://vivoweb.org/ontology/core#hasPublicationVenue> ?revista.
                                ?doc <http://w3id.org/roh/isValidated> 'true'.
                                ?doc <http://purl.org/ontology/bibo/authorList> ?listAuthor.
                                ?listAuthor <http://www.w3.org/1999/02/22-rdf-syntax-ns#comment> ?posicion.
                                ?doc <http://purl.org/dc/terms/issued> ?fecha.  
                                BIND(?fecha/10000000000 as ?anioFecha).
                                ?listAuthor <http://www.w3.org/1999/02/22-rdf-syntax-ns#member> ?person.

                                OPTIONAL{?doc <http://w3id.org/roh/wosCitationCount> ?citasWos.} 
                                OPTIONAL{?doc <http://w3id.org/roh/scopusCitationCount> ?citasScopus.}      
                                OPTIONAL{?doc <http://w3id.org/roh/semanticScholarCitationCount> ?citasSemanticScholar.}

                                ?revista <http://w3id.org/roh/impactIndex> ?indiceImpacto.
                                ?indiceImpacto <http://w3id.org/roh/year> ?anioIndiceImpacto.
                                ?indiceImpacto <http://w3id.org/roh/impactSource> ?fuenteIndiceImpacto.
                                ?fuenteIndiceImpacto <http://purl.org/dc/elements/1.1/title> ?nombreFuenteIndiceImpacto.
                                ?indiceImpacto  <http://w3id.org/roh/impactCategory> ?categoriaIndiceImpacto.
                                ?categoriaIndiceImpacto <http://w3id.org/roh/quartile> ?quartile.
                                ?doc <http://purl.org/dc/elements/1.1/type> ?typeProduccion.
                                ?typeProduccion <http://purl.org/dc/elements/1.1/title> ?tipoProduccion .
                                FILTER(lang(?tipoProduccion )='es')
                                FILTER(?anioIndiceImpacto=?anioFecha)
                                FILTER(lang(?nombreFuenteIndiceImpacto)='es')          

                                """+filter + filter_periodo +"""
                                ?doc <http://purl.org/ontology/bibo/authorList> ?listAuthor2.
                                ?listAuthor2 <http://www.w3.org/1999/02/22-rdf-syntax-ns#member> ?person2.
                                BIND(?person!=?person2 as ?dif)
                            }      }
                """
            )

            try:
                ret = self.sparql.queryAndConvert()
                df = pd.json_normalize(ret["results"]["bindings"])
                try:                
                    df['posicion.value'] = df['posicion.value'].astype(int)
                except:
                    print('Error en la conversión de la posición de los artículos a entero.')
                try:  
                    df['autorUnico.value'] = df['autorUnico.value'].astype(int)
                except:
                    print('Error en la conversión del campo autorUnico a entero.')
                try:
                    df['quartile.value'] = df['quartile.value'].astype(int)
                except:
                    print('Error en la conversión del campo quartile a entero.')
                try:
                    df['citasWos.value'] = df['citasWos.value'].astype(int)
                except Exception as e:
                    print(repr(e))
                    print('Error en la conversión del campo citasWos a entero.')
               

                if(authorship_order):
                    df_sort = df.sort_values(['autorUnico.value','quartile.value','posicion.value','citasWos.value'], ascending=[False, True,True,False])
                else:
                    df_sort = df.sort_values(['quartile.value','citasWos.value'], ascending=[True,False])

                if max_article == 0:
                    max_article = len(df_sort)

                if len(df_sort) < max_article:
                        max_article = len(df_sort)

                if df_sort.iloc[0:max_article] is None:
                    emptyDf = pd.DataFrame()
                    return emptyDf
                else:
                    return df_sort.iloc[0:max_article]
            except Exception as e:
                print(e)
        else:
            print('ERROR al obtener el filter de búsqueda para filtrar por identificador.')
        return pd.DataFrame()

    def get_article(self,id) -> RO:
        """
        Método que obtiene la información de un artículo utilizando su identificador
        :param id identificador
        :return RO objeto con la información del artículo
        """
        self.sparql.setQuery(
        """
        select ?titulo ?doi ?tipoProduccion ?fechaPublicacion ?citasWos ?citasScopus  ?citasSemanticScholar ?volumen ?numero ?paginaInicio ?paginaFin min(?journalNumberInCat) as ?journalNumberInCat min(?publicationPosition) as ?publicationPosition  ?issn ?revista ?editorial ?nombreRevista ?indiceImpacto  min(?cuartil)  as ?cuartil    from <http://gnoss.com/b836078b-78a0-4939-b809-3f2ccf4e5c01>
        where
        {
                    ?doc a 'document'.
                    ?doc <http://purl.org/dc/terms/issued> ?fecha.  
                    OPTIONAL{?doc <http://purl.org/ontology/bibo/volume> ?volumen.}
                    OPTIONAL{?doc <http://purl.org/ontology/bibo/issue> ?numero.}
                    OPTIONAL{?doc <http://purl.org/ontology/bibo/pageStart> ?paginaInicio.}
                    OPTIONAL{?doc <http://purl.org/ontology/bibo/pageEnd> ?paginaFin.}
                    ?doc <http://vivoweb.org/ontology/core#hasPublicationVenue> ?revista.
                    ?revista <http://w3id.org/roh/title> ?nombreRevista.
                    OPTIONAL{?revista <http://purl.org/ontology/bibo/issn> ?issn.}
                    BIND(?fecha/10000000000 as ?anioFecha).
                    ?revista <http://w3id.org/roh/impactIndex> ?impactIndex.
                    OPTIONAL{?revista <http://purl.org/ontology/bibo/editor> ?editorial.}
                    ?impactIndex<http://w3id.org/roh/year> ?anioIndiceImpacto.
                    ?impactIndex<http://w3id.org/roh/impactIndexInYear> ?indiceImpacto.
                    ?impactIndex<http://w3id.org/roh/impactSource> ?fuenteIndiceImpacto.
                    ?fuenteIndiceImpacto <http://purl.org/dc/elements/1.1/title> ?nombreFuenteIndiceImpacto.
                    ?impactIndex<http://w3id.org/roh/impactCategory> ?categoriaIndiceImpacto.
                    ?categoriaIndiceImpacto <http://w3id.org/roh/quartile> ?cuartil .
                    ?categoriaIndiceImpacto <http://w3id.org/roh/journalNumberInCat> ?journalNumberInCat .
                    ?categoriaIndiceImpacto <http://w3id.org/roh/publicationPosition> ?publicationPosition .
                    ?doc <http://w3id.org/roh/title> ?titulo .
                    ?doc <http://purl.org/dc/terms/issued> ?fecha.  
                    OPTIONAL{?doc <http://w3id.org/roh/wosCitationCount> ?citasWos.} 
                    OPTIONAL{?doc <http://w3id.org/roh/scopusCitationCount> ?citasScopus.}      
                    OPTIONAL{?doc <http://w3id.org/roh/semanticScholarCitationCount> ?citasSemanticScholar.} 
                    OPTIONAL{?doc <http://purl.org/ontology/bibo/doi> ?doi.}       
                    BIND( concat(substr(str(?fecha),7,2),'-',substr(str(?fecha),5,2),'-',substr(str(?fecha),1,4)) as ?fechaPublicacion )
                    ?doc <http://purl.org/dc/elements/1.1/type> ?typeProduccion.
                    ?typeProduccion <http://purl.org/dc/elements/1.1/title> ?tipoProduccion .
                    FILTER(lang(?tipoProduccion )='es')
                    FILTER(?anioIndiceImpacto=?anioFecha)
                    FILTER(?doc =<"""+id+""">)
        }
        """
        )
        article:RO = None
        try:
            ret = self.sparql.queryAndConvert()
            df = pd.json_normalize(ret["results"]["bindings"])
            aux = df.iloc[0]

            article = RO(title=aux["titulo.value"],
                publication_type=aux["tipoProduccion.value"],
                position=aux["publicationPosition.value"],
                num_magazines=aux["journalNumberInCat.value"],
                magazine=aux["nombreRevista.value"])
            
            if 'fechaPublicacion.value' in df:
                article.publication_date=aux["fechaPublicacion.value"]
            if 'indiceImpacto.value' in df:
                article.impact=aux["indiceImpacto.value"]
            if 'cuartil.value' in df:
                article.quartile=aux["cuartil.value"]
            if 'citasWos.value' in df:
                article.wos_cites = aux["citasWos.value"]
            if 'doi.value' in df:
                article.doi = aux['doi.value']
            if 'issn.value' in df:
                article.issn = aux["issn.value"]
            if 'paginaInicio.value' in df:
                article.start_page = aux["paginaInicio.value"]
            if 'paginaFin.value' in df:
                article.end_page = aux["paginaFin.value"]
            if 'volumen.value' in df:
                article.volume = aux["volumen.value"]
            if 'editorial.value' in df:
                article.editorial=aux["editorial.value"]
            if 'numero.value' in df:
                article.number = aux["numero.value"]
            if 'citasScopus.value' in df:
                article.scopus_cites = aux["citasScopus.value"]
            if 'citasSemanticScholar.value' in df:    
                article.ss_cites = aux["citasSemanticScholar.value"]

        except Exception as e:
            print(repr(e))
            print('ERROR al obtener un artículo utilizando EDMA.')
        
        return article

    def get_authors_article(self,id):
        """
        Método que obtiene los autores de un artículo
        :param id identificador del artículo
        :return DataFrame objeto respuesta
        """
        self.sparql.setQuery(
        """
        select ?posicion ?autor ?nombreAutor ?emailAutor ?orcidAutor from <http://gnoss.com/b836078b-78a0-4939-b809-3f2ccf4e5c01>
        where
        {
                    ?doc a 'document'.
                    ?doc <http://purl.org/ontology/bibo/authorList> ?listAuthor.
                    ?listAuthor <http://www.w3.org/1999/02/22-rdf-syntax-ns#member> ?autor.
                    ?listAuthor <http://www.w3.org/1999/02/22-rdf-syntax-ns#comment> ?posicion.
                    ?autor <http://xmlns.com/foaf/0.1/name>  ?nombreAutor.
                    OPTIONAL{?autor <http://w3id.org/roh/ORCID> ?orcidAutor .}
                    OPTIONAL{?autor <https://www.w3.org/2006/vcard/ns#email> ?emailAutor .}
                    FILTER(?doc =<"""+id+""">)
        }order by asc(?posicion)
        """
        )

        try:
            ret = self.sparql.queryAndConvert()            
            df = pd.json_normalize(ret["results"]["bindings"])
            return df
        except Exception as e:
            print(e)
        return pd.DataFrame()

    def get_grafo_colaboracion(self,investigador_email) -> pd.DataFrame:
        """
        Método que obtiene el grafo de colaboración de un investigador utilizando su email.
        :param investigador_email email del investigador
        :return DataFrame objeto respuesta
        """
        edma_grafo_colaboracion = """
                SELECT ?person ?nombre ?email count(distinct ?documento) as ?colaboracionesDocumentos  count(distinct ?proy)  as ?colaboracionesProyectos
                count(distinct ?documento)  + count(distinct ?proy) as ?totalColaboraciones
                from <http://gnoss.com/b836078b-78a0-4939-b809-3f2ccf4e5c01>
                WHERE
                {          
                            ?person a 'person'.
                            ?person foaf:name ?nombre.
                            ?person <https://www.w3.org/2006/vcard/ns#email> ?email
                            {
                                        ?documento <http://purl.org/ontology/bibo/authorList> ?listaAutoresA.
                                        ?listaAutoresA <http://www.w3.org/1999/02/22-rdf-syntax-ns#member> ?personaBuscar.
                                        ?documento a 'document'.
                                        ?documento <http://purl.org/ontology/bibo/authorList> ?listaAutores.
                                        ?listaAutores <http://www.w3.org/1999/02/22-rdf-syntax-ns#member> ?person.                     
                            }
                            UNION
                            {       
                                        ?proy <http://w3id.org/roh/membersProject> ?personaBuscar.
                                        ?proy a 'project'.
                                        ?proy <http://w3id.org/roh/membersProject> ?person.                
                            }          
                            FILTER(?person != ?personaBuscar)
                ?personaBuscar a 'person'.
                ?personaBuscar <https://www.w3.org/2006/vcard/ns#email> ?emailPersonaBuscar.
                FILTER( ?emailPersonaBuscar="""+"'"+investigador_email+"'"+""")
                }order by desc(?totalColaboraciones)"""
        try: 
            self.sparql.setQuery(edma_grafo_colaboracion)
            investigadores_colaboradores = self.sparql.query().convert()
            investigadores_colaboradores = investigadores_colaboradores['results']['bindings']
            return pd.json_normalize(investigadores_colaboradores)
        except Exception as e:
            print("Error con EDMA: ",str(e))
            return pd.DataFrame()

    def get_researchers(self):
        """
        Método que obtiene los investigadores de Hércules-ED
        :return DataFrame objeto respuesta
        """
        edma_investigadores = """
        select ?person ?nombrePersona ?email from <http://gnoss.com/document.owl> from <http://gnoss.com/person.owl> from <http://gnoss.com/taxonomy.owl> where { 
            ?doc a <http://purl.org/ontology/bibo/Document>.
            ?doc <http://purl.org/ontology/bibo/authorList> ?autor.
            ?autor <http://www.w3.org/1999/02/22-rdf-syntax-ns#member> ?person.
            ?person <http://xmlns.com/foaf/0.1/name> ?nombrePersona.
            ?person <https://www.w3.org/2006/vcard/ns#email> ?email.
            }GROUP BY ?email 
        """
        try:
            self.sparql.setQuery(edma_investigadores)
            self.sparql.setReturnFormat(JSON)
            investigadores_json = self.sparql.query().convert()
            investigadores_json = investigadores_json['results']['bindings']
            df_investigadores = pd.json_normalize(investigadores_json)
            return df_investigadores
        except Exception as e:
            print("Error al obtener los investigadores de EDMA: ",str(e))
            return pd.DataFrame()

    def get_personaref(self, email):
        """
        Método que obtiene el identificador "personaRef" de un investigador utilizando su email
        :param email email del investigador
        :return str identificador "personaRef"
        """
        edma_investigadores = """
        select ?person ?identifier ?nombrePersona ?email from <http://gnoss.com/document.owl> from <http://gnoss.com/person.owl> from <http://gnoss.com/taxonomy.owl> where { 
            ?doc a <http://purl.org/ontology/bibo/Document>.
            ?doc <http://purl.org/ontology/bibo/authorList> ?autor.
            ?autor <http://www.w3.org/1999/02/22-rdf-syntax-ns#member> ?person.
            ?person <http://w3id.org/roh/crisIdentifier> ?identifier.
            ?person <http://xmlns.com/foaf/0.1/name> ?nombrePersona.
            ?person <https://www.w3.org/2006/vcard/ns#email> ?email.
            FILTER(?email='"""+email+"""')
            }GROUP BY ?email 
        """
        try:
            self.sparql.setQuery(edma_investigadores)
            self.sparql.setReturnFormat(JSON)
            investigadores_json = self.sparql.query().convert()
            investigadores_json = investigadores_json['results']['bindings']
            if len(investigadores_json) == 0:
                return None
            df_investigadores = pd.json_normalize(investigadores_json)
            return df_investigadores.iloc[0]['identifier.value']
            
        except Exception as e:
            print("Error al obtener persona ref de EDMA: ",str(e))
            return None
    
    def get_conferences(self, researcherInfo, period):
        """
        Método encargado de obtener los trabajos presentados en congresos
        de un investigador en base a un período.
        :param researcherInfo información del investigador
        :param period período para filtrar la búsqueda
        :return DataFrame objeto respuesta
        """
        filter = self.get_researcher_filters(researcherInfo)
        filter_period = ''
        if period:
            filter_period = """FILTER(?anioFecha in ("""+period+"""))"""
        if filter:
            self.sparql.setQuery(
            """
            select ?doc from <http://gnoss.com/b836078b-78a0-4939-b809-3f2ccf4e5c01>
            where
            {
                ?doc a 'document'.
                ?doc <http://w3id.org/roh/scientificActivityDocument> <http://gnoss.com/items/scientificactivitydocument_SAD2>.
                ?doc <http://w3id.org/roh/isValidated> 'true'.
                ?doc <http://purl.org/ontology/bibo/authorList> ?listAuthor.
                ?doc <http://purl.org/dc/terms/issued> ?fecha. 
                BIND(?fecha/10000000000 as ?anioFecha).
                ?listAuthor <http://www.w3.org/1999/02/22-rdf-syntax-ns#member> ?person.
                """+filter+filter_period+"""
            }""")

            try:
                ret = self.sparql.queryAndConvert()
                df = pd.json_normalize(ret["results"]["bindings"])
                return df

            except Exception as e:
                print(e)
                print('ERROR al obtener el trabajos presentados en congresos nacionales e internacionales.')
        return pd.DataFrame()

    def get_conference(self, id) -> Conference:
        """
        Método encargado de obtener la información de un congresod
        :param id identificador del congreso
        :return Conference objeto con los datos del congreso
        """
        conference:Conference=None
        if id:
            self.sparql.setQuery(
            """
            select ?titulo ?fechaPublicacion from <http://gnoss.com/b836078b-78a0-4939-b809-3f2ccf4e5c01>
            where
            {
                ?doc a 'document'.
                ?doc <http://w3id.org/roh/title> ?titulo .
                OPTIONAL{?doc <http://purl.org/dc/terms/issued> ?fecha.}
                FILTER(?doc =<"""+id+""">)
            }
            """)

            try:
                ret = self.sparql.queryAndConvert()
                df = pd.json_normalize(ret["results"]["bindings"])
                aux = df.iloc[0]
                conference =  Conference(title=aux["titulo.value"])

                if 'fechaPublicacion.value' in aux:
                    conference.date = aux['fechaPublicacion.value']
                
            except Exception as e:
                print(e)
                print('ERROR al obtener el trabajo ' + id + 'presentado en congresos nacionales e internacionales.')

        else:
            print('ERROR al obtener el filter de búsqueda para filtrar por identificador.')
        return conference

    def get_authors_conference_paper(self,id):
        """
        Método que obtiene los autores de un trabajo presentado en un congreso
        :param id identificador del trabajo
        :return DataFrame objeto respuesta
        """
        self.sparql.setQuery(
        """
        select ?posicion ?autor ?nombreAutor ?emailAutor ?orcidAutor from <http://gnoss.com/b836078b-78a0-4939-b809-3f2ccf4e5c01>
        where
        {
                ?doc a 'document'.

                ?doc <http://purl.org/ontology/bibo/authorList> ?listAuthor.

                ?listAuthor <http://www.w3.org/1999/02/22-rdf-syntax-ns#member> ?autor.

                ?listAuthor <http://www.w3.org/1999/02/22-rdf-syntax-ns#comment> ?posicion.

                ?autor <http://xmlns.com/foaf/0.1/name>  ?nombreAutor.

                OPTIONAL{?autor <http://w3id.org/roh/ORCID> ?orcidAutor .}

                OPTIONAL{?autor <https://www.w3.org/2006/vcard/ns#email> ?emailAutor .}

                FILTER(?doc =<"""+id+""">)
        }order by asc(?posicion)
        """
        )

        try:
            ret = self.sparql.queryAndConvert()            
            df = pd.json_normalize(ret["results"]["bindings"])
            return df
        except Exception as e:
            print(e)
        return pd.DataFrame()

    def get_researcher_patents(self, researcherInfo, period):
        """
        Método que obtiene las patentes de un investigador en base a un período de años.
        :param researcherInfo información relacionada con el investigador
        :param period cadena de años separada por comas
        :return Dataframe respuesta con la información solicitada
        """
        filter = self.get_researcher_filters(researcherInfo)
        filter_period = ''
        if period:
            filter_period = """FILTER(?anioFecha in ("""+period+"""))"""

        if filter:
            self.sparql.setQuery(
            """
            select ?doc from <http://gnoss.com/b836078b-78a0-4939-b809-3f2ccf4e5c01> where
            {
                ?doc a 'patent'.
                ?doc <http://w3id.org/roh/isValidated> 'true'.
                ?doc <http://purl.org/ontology/bibo/authorList> ?listAuthor.
                ?doc <http://purl.org/dc/terms/issued> ?fecha. 
                BIND(?fecha/10000000000 as ?anioFecha).
                ?listAuthor <http://www.w3.org/1999/02/22-rdf-syntax-ns#member> ?person.
                """+filter+filter_period+"""
            }""")
            try:
                ret = self.sparql.queryAndConvert()
                df = pd.json_normalize(ret["results"]["bindings"])
                return df
            except Exception as e:
                print(e)
                print('ERROR al obtener las patentes.')
        else:
            print(
                'ERROR al obtener el filter de búsqueda para filtrar por identificador.')
        return pd.DataFrame()

    def get_title_date_patent(self, id) -> Patent:
        """
        Método para obtener el título y la fecha de una patente
        :param id identificador de la patente
        :return Patente objeto con los datos obtenidos
        """
        try:
            self.sparql.setQuery(
                """
                select ?titulo ?fechaPublicacion from <http://gnoss.com/b836078b-78a0-4939-b809-3f2ccf4e5c01>
                where
                {
                    ?doc a 'patent'.
                    ?doc <http://w3id.org/roh/title> ?titulo .
                    OPTIONAL{?doc <http://purl.org/dc/terms/issued> ?fecha. }
                    FILTER(?doc =<"""+id+""">)
                }
                """)

            ret = self.sparql.queryAndConvert()
            df = pd.json_normalize(ret["results"]["bindings"])

            aux = df.iloc[0]
            patent = Patent(title=aux["titulo.value"])            
            if 'fechaPublicacion.value' in df:
                patent.date=aux["fechaPublicacion.value"]

            return patent

        except Exception as e:
            print(repr(e))
            print('ERROR enla obtención del título y fecha de la patente con identificador: ' + id)
        return None

    def get_authors_patent(self, id):
        """
        Método para obtener la lista de autores de una patente
        :param id identificador de la patente
        :return DataFrame dataframe con los datos obtenidos
        """
        try:
            self.sparql.queryAndConvert(
            """
            select ?posicion ?autor ?nombreAutor ?emailAutor ?orcidAutor from <http://gnoss.com/b836078b-78a0-4939-b809-3f2ccf4e5c01>
            where
            {
                ?doc a 'document'.
                ?doc <http://purl.org/ontology/bibo/authorList> ?listAuthor.
                ?listAuthor <http://www.w3.org/1999/02/22-rdf-syntax-ns#member> ?autor.
                ?listAuthor <http://www.w3.org/1999/02/22-rdf-syntax-ns#comment> ?posicion.
                ?autor <http://xmlns.com/foaf/0.1/name>  ?nombreAutor.
                OPTIONAL{?autor <http://w3id.org/roh/ORCID> ?orcidAutor .}
                OPTIONAL{?autor <https://www.w3.org/2006/vcard/ns#email> ?emailAutor .}
                FILTER(?doc =<"""+id+""">)
            }order by asc(?posicion)
            """)
            
            ret = self.sparql.queryAndConvert()
            df = pd.json_normalize(ret["results"]["bindings"])
            return df  

        except Exception as e:
            print(repr(e))
            print('ERROR enla obtención la lista de autores de la patente con identificador: ' + id)
        return pd.DataFrame()