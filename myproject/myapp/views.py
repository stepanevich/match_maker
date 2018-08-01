# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.conf import settings
import cv2
import numpy as np
import scipy
from scipy.misc import imread
import pickle
import random
import os
import matplotlib.pyplot as plt

from myproject.myapp.models import Document
from myproject.myapp.forms import DocumentForm, ImageForm

def extract_features(image_path, vector_size=32):
    image = imread(image_path, mode="RGB")
    try:
        # Using KAZE, cause SIFT, ORB and other was moved to additional module
        # which is adding addtional pain during install
        alg = cv2.KAZE_create()
        # Dinding image keypoints
        kps = alg.detect(image)
        # Getting first 32 of them. 
        # Number of keypoints is varies depend on image size and color pallet
        # Sorting them based on keypoint response value(bigger is better)
        kps = sorted(kps, key=lambda x: -x.response)[:vector_size]
        # computing descriptors vector
        kps, dsc = alg.compute(image, kps)
        # Flatten all of them in one big vector - our feature vector
        dsc = dsc.flatten()
        # Making descriptor of same size
        # Descriptor vector size is 64
        needed_size = (vector_size * 64)
        if dsc.size < needed_size:
            # if we have less the 32 descriptors then just adding zeros at the
            # end of our feature vector
            dsc = np.concatenate([dsc, np.zeros(needed_size - dsc.size)])
    except cv2.error as e:
        print ('Error: ', e)
        return None

    return dsc

class Matcher(object):

    def __init__(self, data):
        self.data = data
        self.names = []
        self.matrix = []
        for k, v in self.data.items():
            self.names.append(k)
            self.matrix.append(v)
        self.matrix = np.array(self.matrix)
        self.names = np.array(self.names)

    def cos_cdist(self, vector):
        # getting cosine distance between search image and images database
        v = vector.reshape(1, -1)
        return scipy.spatial.distance.cdist(self.matrix, v, 'cosine').reshape(-1)

    def match(self, image_path, topn=1000):
        features = extract_features(image_path)
        img_distances = self.cos_cdist(features)
        # getting top 5 records
        nearest_ids = np.argsort(img_distances)[:topn].tolist()
        nearest_img_paths = self.names[nearest_ids].tolist()

        return nearest_img_paths, img_distances[nearest_ids].tolist()

def list(request):
    # Handle file upload
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            picture = form.save()
            print(picture.docfile)
            file = os.path.join(settings.MEDIA_ROOT, picture.docfile.name)
            
            result = {}
            print ('Extracting features from image %s' % file)
            name = file.split('/')[-1].lower()
            result[name] = extract_features(file)
            picture.features = pickle.dumps(result)
            picture.save()

            # Redirect to the document list after POST
            return HttpResponseRedirect(reverse('list'))
    else:
        form = DocumentForm()  # A empty, unbound form

    # Load documents for the list page
    documents = Document.objects.all()

    # Render list page with the documents and the form
    return render(
        request,
        'list.html',
        {'documents': documents, 'form': form}
    )

def filename(request):
    pair ={}
    results = []
    # Handle file upload
    if request.method == 'POST':
        form = ImageForm(request.POST, request.FILES)
        if form.is_valid():
            #newdoc = Document(docfile=request.FILES['docfile'])
            #newdoc.save()
            #picture = Document.objects.get(name = picture_name)
            documents = Document.objects.all()
            documents_dict = {}
            features = {}
            names = []
            for i in documents:
                name = i.docfile.name.split('/')[-1].lower()
                names.append(name)
                features[name] = pickle.loads(i.features)[(i.docfile.name).lower()]
                documents_dict[name] = i
            #names.append(request.FILES['docfile'].name)
            file = os.path.join(settings.MEDIA_ROOT, request.FILES['docfile'].name) 
            print(file)
            files = [os.path.join(settings.MEDIA_ROOT, p) for p in names]
            #print ('Extracting features from image %s' % file)
            #name = file.split('/')[-1].lower()
            #features[name] = extract_features(file)
            #print(features)
            #print(len(files))
            
            ma = Matcher(features)

            print ('Query image ==========================================')
            names, match = ma.match(file)
            print ('ЭТО documents_dict')
            print (documents_dict)
            pair = zip(names,match)
            list_pair = sorted(pair, key=lambda x: x[-1])
            for n, w in list_pair:
                documents_dict[n].weight = w
                results.append(documents_dict[n])
                print('Wheight %s' % (1-w))
            print ('Result images ========================================')
            #print (names)
            #print (match)
            for m in range(len(files)):
                print ('Match %s' % (1-match[m]))
    else:
        form = DocumentForm()  # A empty, unbound form


    # Render list page with the documents and the form
    return render(
        request,
        'filename.html',
        {'form': form,
         'documents': results}
    )  