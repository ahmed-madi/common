from common.api.controllers.company.activity import ActivityResource
from common.api.controllers.company.event import EventResource
from common.api.controllers.company.newsletter import CompanyNewsletterResource
from common.api.controllers.company.organizational_chart import OrganizationalChartResource

company_rules = []
company_rules += ActivityResource.get_routes()
company_rules += EventResource.get_routes()
company_rules += CompanyNewsletterResource.get_routes()
company_rules += OrganizationalChartResource.get_routes()
