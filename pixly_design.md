
App design   backend: Python-flask-jinja   frontend: jinja templates - js

get /                               home page simple html

post /imgaes/upload                 upload an image

get /images                         see all of the images

get /images/:id                     visit a specific photo, allow downloading this image

get/post  /imgaes/:id/edit          edit an image, option to upload the edited image 






Database design: psql

table: images

fields: id, locaation, camera_model... img_url(s3)