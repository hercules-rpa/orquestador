from flask                              import Blueprint, abort, request
from flask.wrappers                     import Response
from flask_restful                      import Api, Resource
from rpa_orchestrator.orchestrator    import Orchestrator
from marshmallow                        import Schema, fields
from flask_apispec                      import marshal_with,doc
from flask_apispec.views                import MethodResource
from model.DocInfo                      import DocInfo

orch = Orchestrator()

stat_v1_0_bp = Blueprint('stat_v1_0_bp', __name__)
api = Api(stat_v1_0_bp)

def getBlueprint():
    return stat_v1_0_bp

class StatisticsDashBoardSchema(Schema):
    """
    Clase esquema para representar las estadísticas en la página principal del dashboard.
    """
    execution_day_week = fields.List(fields.Int())
    execution_day_month = fields.List(fields.Int())
    execution_month_year = fields.List(fields.Int())
    robots_online = fields.Int()
    process_actives = fields.Int()
    process_problems = fields.Int()
    process_completed = fields.Int()

class MainStatisticsResource(MethodResource, Resource):
    @doc(description='Obtener estadísticas principales para la página dashboard', tags=['StatsDashBoard'])
    @marshal_with(StatisticsDashBoardSchema)
    def get(self):
        """
        Método para obtener las estadísticas del Dashboard.
        """
        return Response(orch.get_main_stats(), status=201, mimetype='application/json')

def getDocInfo():
    """
    Método abstracto para crear las entradas en Swagger.
    """
    doc_info_list = []
    ep1 = DocInfo(doc_class = MainStatisticsResource, doc_blueprint='stat_v1_0_bp', doc_endpoint='stats_maindashboard_resource')
    doc_info_list.append(ep1)
    return doc_info_list

api.add_resource(MainStatisticsResource,'/api/orchestrator/statistics/maindashboard',endpoint='stats_maindashboard_resource' )
