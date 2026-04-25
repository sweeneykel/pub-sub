from AnnotationDBModule import client, db, collection

for x in collection.find():
  print(x)
