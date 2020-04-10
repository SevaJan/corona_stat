main.py: парсер, который вытаскивает с сайтов https://www.worldometers.info/coronavirus/ и https://xn--80aesfpebagmfblc0a.xn--p1ai/ данные о коронавирусе. Написан с помощью https://towardsdatascience.com/coronavirus-track-coronavirus-in-your-country-by-displaying-notification-c914b5652088;

virtualenv: виртуальное окружение, создаётся по гайду https://cloud.ibm.com/docs/openwhisk?topic=cloud-functions-prep#prep_python_local_virtenv;

statistics.zip: zip файл, в котором заархивированы main.py и virtualenv.

Чтобы бот обращался к IBM Cloud Functions, нужно включить Webhooks, в скилле указать URL и добавить CF-based API key for this namespace.
