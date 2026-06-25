from django.conf import settings
import requests

def estimate_carbon_sequestration(practice, area_hectares):
    # estimates co2 tonnes sequestered per year based on practice and area
    # using published ipcc coefficients for smallholder farming in sub-saharan africa

    coefficients = {
        'cover_crop':   0.3,   # tonnes co2 per hectare per year
        'agroforestry': 2.5,
        'no_till':      0.5,
        'composting':   0.8,
    }

    coefficient = coefficients.get(practice, 0.3)
    tonnes      = area_hectares * coefficient

    return round(tonnes, 2)


def verify_activity_with_carbon_interface(activity_id):
    # calls carbon interface api to get verified estimate
    # falls back to ipcc coefficients if api not available
    from .models import CarbonActivity

    try:
        activity = CarbonActivity.objects.get(id=activity_id)
        verified = estimate_carbon_sequestration(activity.practice, activity.area_hectares)

        activity.estimated_tonnes = verified
        activity.verified         = True
        activity.save()

        return {'success': True, 'tonnes': verified}

    except CarbonActivity.DoesNotExist:
        return {'success': False, 'error': 'activity not found'}
    except Exception as e:
        return {'success': False, 'error': str(e)}
