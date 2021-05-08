from django.http import HttpResponse

from .FCMManager import sendPush


def sendNotification(request):
    tokens = ["ei-Qxh3FRPK17QQnhyyMZp:APA91bGkoNekZACN-5317AQvHngErIQsTx2b5vCkCnk4W770avNLMTXc0xb022hsylKUcnLJ89yjEiGc0afc1eFkvWPMAKMMEaafA8aZz2eXK8wbx102T0GQa58xptBLnITl98cTU8Iv"
        # ,"c5zCzCU8TO-IJfVxD7g1JX:APA91bHtp4RnrjWAi6mzgGUCV_K9wrlr_O03Xn_KyPRYyOE3T5RW3dGHjdLfvrFXHwkPtY7TQOUyMiUrYEbw_Nyb_0efIiHpb-4VSJVMeYWkE1cLEaNAa85K0tlOMNlDqS_oLVy-SdYe"
        # ,"evOISh8zTp-kt2VI4G_JRa:APA91bGI6sbpKLdziEBnrr2AtBS1lXYmgJYy61Z081wWZ9f8G2LHiH_Tk-bm0mZ9B9UTnjGtJfKZabQGf0LOrdClFnHMGzJNw2Q1ilX3oj_TJR0LfPrIIR5F2YMzRV1vCqGCyCJ_k36s"
        # ,"cTdgTuntS2KtzBVLShswu5:APA91bGJXS2ApEXOzBo-CMtV9UWjua7YhnYFFPv1fDx1tVIvVY-9QxRSPJX0tiOoGh0RcW7MtvHrxgC7FPp5xjPgocdxt_TnhKjP0crapOppxLZEsYDipT5Xk5Aj412rsKg83lnCnKBN"
        ]
    sendPush("Hi", "testing, meesage from vamsi", tokens)
    return HttpResponse("success", 200)
