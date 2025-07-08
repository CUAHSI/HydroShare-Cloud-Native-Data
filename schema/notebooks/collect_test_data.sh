#!/bin/bash


mkdir -p data

wget -P data https://www.hydroshare.org/django_irods/download/bags/24a191169881433d9f894f896eba5263.zip

unzip -j data/24a191169881433d9f894f896eba5263.zip -d data

rm data/24a191169881433d9f894f896eba5263.zip
