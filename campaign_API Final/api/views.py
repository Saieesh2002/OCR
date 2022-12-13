from django.views import View
from django.http import JsonResponse
import json
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from .ocr_azure import ocr_data



@method_decorator(csrf_exempt, name='dispatch')
class Ocr(View):
    def post(self, request):

        data = json.loads(request.body.decode("utf-8"))
        print("data ----> ",data)

        img_url = data['url']

        result = ocr_data(img_url)

        data = {
            "result": result,
        }
        return JsonResponse(data, status=201)

