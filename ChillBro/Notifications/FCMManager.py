# import firebase_admin
# from firebase_admin import credentials, messaging

# cred = credentials.Certificate({
#   "type": "service_account",
#   "project_id": "cpanel-d9258",
#   "private_key_id": "6fc53389a33ee2f79159705db7508b1962cb5975",
#   "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQDEXzca5RLmsff1\n/gu/ar7xjogxjFAy/M6OY0uaJnCHG2kLpQs7jrtunO3b18p8jvJBA/+aJsdI37q1\nJoo5jdvAedZCYckIiQvRY7j7zMAoxu04Qi6ixnroAvyas5002hPoYJXNHllQaWQh\nrysOhUIcdlHMDsZ/Mwn+IxHFgBL9lrjaR7N50tHl7jvvrq1StHeicAAD1zlSbHZk\npFOYMYyehb89VKzzN+OCgITuDJuttXiouMjckNJMtGMEXRCshPg7t90YRTjayVwf\nFzVVyudXkipyXgc69iK1PBnCsf3e68DgiSu/oy6no64vPCaZsWXEXI7CdQXsyhCH\n5fVtubpJAgMBAAECggEABVrHeYOPUOx/qMzQecaHAMvMitWrBAGTftELk9Sc6ybh\nezHZCnAqts+PPK2dIylxMY9oD1D5Ib4zB23uz+FebC34/Gam87qr8IiF9+drgnkj\n07hvRdzrEfZEjdHcaqoQfVIb55kpIY7mzh8qXwXIdEGlhZlOCul4/2hp+28R0CnD\n7r+D+w/Td1jrkFEvxwHodWP7LFnwV/ipzMjqbETCyH1l5RBLEpXt6QtubIAFYsOf\noVFTfWpzIshbacXu9zCGyM12qTh+VF+kBOt6RJ3eDQ8RqjkUjV2qk0O3ZyoJYLrr\nZj5pkJd5mIpaNzbBV82hifa6QB/vy2FFZlzGqCEF8QKBgQDteTofiCAjH7H5Df/R\nxvZB2lQS6izqsS99EbTIgbTophev52ZxrFErRsnw2VkBV1U4ETnMh1WSb7lYsqSa\nDOSoqq5rhZ3LM76RWdJ0gIzDzEdiY565Fx0HAsLQCV3n2iWJ0frKRP7FNhlh4PYa\nXWPoiUb4X9YUztPWkJE4cu4K8QKBgQDTsR2ElL+HnIj5bJdVI+rWou/97sM/QseG\n4LhHApJ6sH8lwR3x/wqa8Q8bj44qFlcfg71Bw6igyF78POMf620mL072bpkAEhe0\nylezkxHu3HtUjCeMZDKBvs+9yc+vE5/DRc6v7wSgpEPuDCFnDk3bpSlEG3TtKwMr\nL5k17FG02QKBgCn4lhRCm+N5U5xAJCmwb4++BcP+DYhBXrJNMdWKTy4bRO57CHko\nyoPKlCB0Wa3KAK7TJJMIjFBAXNLXaA4uHy/MUt2AFR53+8N2y6J5oedtMGSsVL5D\n3oaBr2rTbPxwatgL+7ZKMXkrkZriBr0sKl9L+/YkAhNVZs1yaag/b+ERAoGANglb\nCJHTxjEeAdVHV/NgKcPT0RUWf9pzBinswCuW6nyNKD0AgNpigaSQ/68IUhP7z06Y\ni+X+8HPVUzvTmj1FUl73IA6hPZRgusR/2JXtGPTtAmr4WWzmO5pSexa9zeoLeRQj\nq2Mu4jasJGKyUBUlqLCjNQBxO20kVOzEhjA5txkCgYEAqGOSvla6z4NlZPUbwCJ7\nGPlgSLv4582MUpRogFP8vwKLwYO6VCDT3M2PHP6BZvLlfeGbgGgg9GsPuz0PdTvO\nhFbgIChgZM8UzsVsNLHMFMc3XDpLAfIiFeieEgGqBz9JkiJIqiVSpRf40Q+CH+d5\nvPAnHNbrxyf2ohnwFH9b8z0=\n-----END PRIVATE KEY-----\n",
#   "client_email": "firebase-adminsdk-uzsvl@cpanel-d9258.iam.gserviceaccount.com",
#   "client_id": "116974782270936659735",
#   "auth_uri": "https://accounts.google.com/o/oauth2/auth",
#   "token_uri": "https://oauth2.googleapis.com/token",
#   "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
#   "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-uzsvl%40cpanel-d9258.iam.gserviceaccount.com"
# }
# )
# firebase_admin.initialize_app(cred)


def sendPush(title, msg, registration_token, dataObject = None):
    # message = messaging.MulticastMessage(
    #     notification=messaging.Notification(
    #         title=title,
    #         body=msg
    #     ),
    #     data=dataObject,
    #     tokens=registration_token,
    # )
    #
    # response = messaging.send_multicast(message)
    # return response

    pass
