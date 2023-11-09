import paho.mqtt.client as mqtt
from django.conf import settings
from django.shortcuts import render

import paho.mqtt.client as mqtt
import json

# Defina a função de callback para processar mensagens recebidas
# def on_message(client, userdata, message):
#     payload = json.loads(message.payload)
#     # Aqui você pode adicionar lógica para atualizar o front-end com as mensagens recebidas

# # Configuração do cliente MQTT
# client = mqtt.Client()
# client.on_message = on_message

# # Conecte-se ao broker MQTT
# def connect_mqtt():
#     client.connect("mqtt-dashboard.com", 1883)  # Substitua "endereço_do_broker" pelo seu endereço MQTT
#     client.subscribe("Unifesp-ICT MQTT Topic I4O592")  # Substitua "tópico" pelo tópico desejado
#     client.loop_start()

# # Desconecte-se do broker MQTT
# def disconnect_mqtt():
#     client.loop_stop()
#     client.disconnect()



# def on_connect(mqtt_client, userdata, flags, rc):
#    if rc == 0:
#        print('Connected successfully')
#        mqtt_client.subscribe('Unifesp-ICT MQTT Topic I4O592')
#    else:
#        print('Bad connection. Code:', rc)


# def on_message(mqtt_client, userdata, msg):
#     global valor_mqtt
#     valor_mqtt = (msg.payload)
#     print(valor_mqtt)

# def print_on_m(request):
#   global valor_mqtt
#   message = str(valor_mqtt)
#   return render(request, 'pages/index.html',{'context':message})

# client = mqtt.Client()
# client.on_connect = on_connect
# client.on_message = on_message
# client.username_pw_set(settings.MQTT_USER, settings.MQTT_PASSWORD)
# client.connect(
#     host=settings.MQTT_SERVER,
#     port=settings.MQTT_PORT,
# )