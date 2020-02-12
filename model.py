from keras.models import model_from_json, load_model
from keras.models import Model, Sequential

model = load_model('C:\\inetpub\\wwwroot\\model.h5')
model.load_weights('C:\\inetpub\\wwwroot\\vgg_face_weights.h5')
vgg_face_descriptor = Model(inputs=model.layers[0].input, outputs=model.layers[-2].output)

