
from enum import Flag

"""
TipoIdentificadorInvestigador es un flag que identifica el tipo de identificador 
del investigador
"""
class ResearcherIdentifyType(Flag):
        NODEFINIDO = 0
        PERSONAREF = 1
        EMAIL = 2
        ORCID = 3