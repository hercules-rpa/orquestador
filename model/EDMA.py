from SPARQLWrapper import SPARQLWrapper, JSON
import pandas as pd
from model.process.Proceso2.Entities.Congreso import Congreso
from model.process.Proceso2.Entities.DatosInvestigador import DatosInvestigador
from model.process.Proceso2.Entities.Enumerados.TipoIdentificadorInvestigador import TipoIdentificadorInvestigador
from model.process.Proceso2.Entities.RO import RO

class EDMA():
    HOST = "http://82.223.242.49:8890"
    IP = "82.223.242.49"
    EDMA_ENDPOINT = "http://82.223.242.49:8890/sparql"

    def __init__(self):
        self.sparql = SPARQLWrapper(self.EDMA_ENDPOINT)
        self.sparql.setReturnFormat(JSON)

    def get_all_articles(self, start_date: str, end_date: str):
        filtro = "FILTER(?aniomesdia>=" + start_date + " AND ?aniomesdia<=" + end_date + ")"
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

                 """+ filtro +"""
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

    def get_oferta_tecnologica(self, start_date: str, end_date: str):
        filtro = "FILTER(?fecha>="+start_date+" && ?fecha <=" +end_date+")"
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

            """+ filtro +"""
            }order by desc(?fecha) desc(?s)
            """
        )

        try:
            ret = self.sparql.queryAndConvert()
            df = pd.json_normalize(ret["results"]["bindings"])
            return df
        except Exception as e:
            print(e)
            print('ERROR en la obtención de oferta tecnológica')
        return pd.DataFrame()


    def get_datos_investigador(self, infoInvestigador) -> DatosInvestigador:
        """
        Método que obtiene los datos del investigador en base a un tipo de identificador y a un id.
        """
        filtro = self.get_filtro_investigador(infoInvestigador)
        if filtro:
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
            """ + filtro + """                
            }
            """
            )

            try:
                ret = self.sparql.queryAndConvert()
                df = pd.json_normalize(ret["results"]["bindings"])
                if not df.empty:
                    datosInvestigador = DatosInvestigador()
                    datosInvestigador.set_properties(df)
                    return datosInvestigador
            except Exception as e:
                print(e)
                print('ERROR al tratar los parámetros de los datos del investigador')
        else:
            print(
                'ERROR al obtener el filtro de búsqueda para filtrar por identificador.')
        return None

    def get_capitulos_libros(self, infoInvestigador, periodo):
        """
        Método qude obtiene los capítulos de libros de un investigador en base a un período de años.
        """
        filtro = self.get_filtro_investigador(infoInvestigador)
        filtro_periodo = ''
        if periodo:
            filtro_periodo = """FILTER(?anioFecha in ("""+periodo+"""))"""
        if filtro:
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

                            """+filtro+filtro_periodo+"""
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
                'ERROR al obtener el filtro de búsqueda para filtrar por identificador.')
        return pd.DataFrame()

    def get_filtro_investigador(self, infoInvestigador: tuple) -> str:
        """
        Método encargado de obtener el filtro de un investigador en base al tipo de identificador y al identificador.
        """
        if infoInvestigador:
            if infoInvestigador[0] == TipoIdentificadorInvestigador.PERSONAREF:
                return """?person <http://w3id.org/roh/crisIdentifier> ?identifier.
                        FILTER(?identifier='"""+infoInvestigador[1]+"""')"""

            if infoInvestigador[0] == TipoIdentificadorInvestigador.ORCID:
                return """?person <http://w3id.org/roh/ORCID> ?orcid.
                        FILTER(?orcid='"""+infoInvestigador[1]+"""') """

            if infoInvestigador[0] == TipoIdentificadorInvestigador.EMAIL:
                return """?person <https://www.w3.org/2006/vcard/ns#email> ?email.
                        FILTER(?email='"""+infoInvestigador[1]+"""')"""

        return None

    def get_libros(self, infoInvestigador, periodo):
        """
        Método encargado de obtener los libros de un investigador en base a un período.
        """
        filtro = self.get_filtro_investigador(infoInvestigador)
        filtro_periodo = ''
        if periodo:
            filtro_periodo = """FILTER(?anioFecha in ("""+periodo+"""))"""
        if filtro:
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

                            """+filtro+filtro_periodo+"""
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
            print('ERROR al obtener el filtro de búsqueda para filtrar por identificador.')
        return pd.DataFrame()

    
    def get_lista_articulos_investigador(self,infoInvestigador, max_article:int, periodo, autoria_orden):
        """
        Método que obtiene la lista de artículos de un investigador.
        """
        filtro = self.get_filtro_investigador(infoInvestigador)
        filtro_periodo = ''
        if periodo:
            filtro_periodo = """FILTER(?anioFecha in ("""+periodo+"""))"""
        if filtro:
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

                                """+filtro + filtro_periodo +"""
                                ?doc <http://purl.org/ontology/bibo/authorList> ?listAuthor2.
                                ?listAuthor2 <http://www.w3.org/1999/02/22-rdf-syntax-ns#member> ?person2.
                                BIND(?person!=?person2 as ?dif)
                            }
            }
                """
            )

            try:
                ret = self.sparql.queryAndConvert()
                df = pd.json_normalize(ret["results"]["bindings"])
                
                df['posicion.value'] = df['posicion.value'].astype(int)
                df['autorUnico.value'] = df['autorUnico.value'].astype(int)
                df['quartile.value'] = df['quartile.value'].astype(int)
                df['citasWos.value'] = df['citasWos.value'].astype(int)

                if(autoria_orden):
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
            print('ERROR al obtener el filtro de búsqueda para filtrar por identificador.')
        return pd.DataFrame()

    def get_articulo(self,id_articulo) -> RO:
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
                    FILTER(?doc =<"""+id_articulo+""">)
        }
        """
        )

        try:
            ret = self.sparql.queryAndConvert()
            df = pd.json_normalize(ret["results"]["bindings"])
            aux = df.iloc[0]
            articulo = RO(titulo=aux["titulo.value"],tipo_publicacion=aux["tipoProduccion.value"],
            fecha_publicacion=aux["fechaPublicacion.value"], wos_cites=aux["citasWos.value"],
            posicion=aux["publicationPosition.value"],n_revistas=aux["journalNumberInCat.value"],
            revista=aux["nombreRevista.value"],impacto=aux["indiceImpacto.value"],cuartil=aux["cuartil.value"])
            
            if 'doi.value' in df:
                articulo.doi = aux['doi.value']
            if 'issn.value' in df:
                articulo.issn = aux["issn.value"]
            if 'paginaInicio.value' in df:
                articulo.pag_inicio = aux["paginaInicio.value"]
            if 'paginaFin.value' in df:
                articulo.pag_fin = aux["paginaFin.value"]
            if 'volumen.value' in df:
                articulo.volumen = aux["volumen.value"]
            if 'editorial.value' in df:
                articulo.editorial=aux["editorial.value"]
            if 'numero.value' in df:
                articulo.numero = aux["numero.value"]
            if 'citasScopus.value' in df:
                articulo.scopus_cites = aux["citasScopus.value"]
            if 'citasSemanticScholar.value' in df:    
                articulo.ss_cites = aux["citasSemanticScholar.value"]

            return articulo
        except Exception as e:
            print(e)
            print('ERROR al obtener un artículo utilizando EDMA.')
        return None

    def get_autores_articulo(self,id_articulo):
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
                    FILTER(?doc =<"""+id_articulo+""">)
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
        edma_grafo_colaboracion = """
                SELECT ?person ?nombre ?email count(distinct ?documento) as ?colaboracionesDocumentos  count(distinct ?proy)  as ?colaboracionesProyectos
                count(distinct ?documento)  + count(distinct ?proy) as ?totalColaboraciones
                from <http://gnoss.com/b836078b-78a0-4939-b809-3f2ccf4e5c01>
                WHERE
                {          
                            ?person a 'person'.
                            ?person foaf:name ?nombre.
                        OPTIONAL{?person <https://www.w3.org/2006/vcard/ns#email> ?email}  
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

    def get_investigadores(self):
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
    def get_trabajos_congresos(self, infoInvestigador, periodo):
        """
        Método encargado de obtener los trabajos presentados en congresos
        de un investigador en base a un período.
        """
        filtro = self.get_filtro_investigador(infoInvestigador)
        filtro_periodo = ''
        if periodo:
            filtro_periodo = """FILTER(?anioFecha in ("""+periodo+"""))"""
        if filtro:
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
                """+filtro+filtro_periodo+"""
            }""")

            try:
                ret = self.sparql.queryAndConvert()
                df = pd.json_normalize(ret["results"]["bindings"])
                return df

            except Exception as e:
                print(e)
                print('ERROR al obtener el trabajos presentados en congresos nacionales e internacionales.')
        return pd.DataFrame()

    def get_trabajo_congreso(self, id) -> Congreso:
        """
        Método encargado de obtener los trabajos presentados en congresos
        de un investigador en base a un período.
        """
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
                congreso =  Congreso(titulo=aux["titulo.value"])

                if 'fechaPublicacion.value' in aux:
                    congreso.fecha = aux['fechaPublicacion.value']
                
                return congreso

            except Exception as e:
                print(e)
                print('ERROR al obtener el trabajo ' + id + 'presentado en congresos nacionales e internacionales.')

        else:
            print('ERROR al obtener el filtro de búsqueda para filtrar por identificador.')
        return None

    def get_autores_trabajo_congreso(self,id):
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
