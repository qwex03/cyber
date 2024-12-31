import requests
import os
import pandas as pd
import tensorflow as tf
import cv2
import numpy as np
from scipy.spatial.distance import cdist
from sklearn.preprocessing import StandardScaler




# Charger le modèle ResNet50 pré-entraîné (sans les couches de classification)
model = tf.keras.applications.ResNet50(weights='imagenet', include_top=False, pooling='avg')


# Fonction pour prétraiter une image
def preprocess_image(image_path):
    image = cv2.imread(image_path)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    image_resized = cv2.resize(image, (224, 224))
    image_normalized = image_resized / 255.0
    image_input = np.expand_dims(image_normalized, axis=0)
    return image_input


# Fonction pour extraire les caractéristiques d'une image
def extract_features(image_path, scaler=None):
    image_input = preprocess_image(image_path)
    features = model.predict(image_input)
    features =  features.flatten()


    if scaler:
            features = scaler.transform([features])[0]
       
    return features


# Votre clé API Flickr
API_KEY = "ad379085f8a136a8e3117dcb62d376a1"
SEARCH_URL = "https://api.flickr.com/services/rest/"


# Dossier de téléchargement des images
OUTPUT_DIR = r"C:\Users\mariu\Desktop\Cours\ProjetImage\test-v3\flickr_images"
os.makedirs(OUTPUT_DIR, exist_ok=True)


# Fonction pour rechercher des images géolocalisées avec des tags spécifiques
def search_flickr_images(query, tags=None, num_images=100, min_upload_date="2020-01-01"):
    params = {
        "method": "flickr.photos.search",
        "api_key": API_KEY,
        "format": "json",
        "nojsoncallback": 1,
        "text": query,
        "has_geo": 1,
        "extras": "geo,url_o",
        "per_page": num_images,
        "min_upload_date": min_upload_date,
    }
   
    # Ajouter les tags à la requête si fournis
    if tags:
        params["tags"] = tags
   
    response = requests.get(SEARCH_URL, params=params)
    response_json = response.json()
   
    if "photos" in response_json:
        return response_json["photos"]["photo"]
    return []


# Télécharger une image et renvoyer son chemin local
def download_image(photo, output_dir):
    if "url_o" not in photo:
        return None
    url = photo["url_o"]
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        photo_id = photo["id"]
        file_path = os.path.join(output_dir, f"{photo_id}.jpg")
        with open(file_path, "wb") as file:
            file.write(response.content)
        return file_path
    return None


# Récupérer les images et leurs coordonnées GPS
def fetch_images_with_geo(query, tags=None, num_images=100):
    photos = search_flickr_images(query, tags=tags, num_images=num_images)
    image_data = []
   
    for photo in photos:
        lat, lon = photo.get("latitude"), photo.get("longitude")
        if not lat or not lon:
            continue
       
        # Télécharger l'image
        local_path = download_image(photo, OUTPUT_DIR)
        if local_path:
            image_data.append({
                "image_path": local_path,
                "latitude": float(lat),
                "longitude": float(lon),
            })
   
    return image_data


# Extraire les caractéristiques et sauvegarder dans un CSV
def save_flickr_features_to_csv(image_db, output_file):
    rows = []
    for entry in image_db:
        features = extract_features(entry["image_path"])  # Utilise votre fonction existante
        location = (entry["latitude"], entry["longitude"])
        rows.append({
            "features": list(features),
            "latitude": location[0],
            "longitude": location[1]
        })
   
    # Convertir les données en DataFrame pandas
    df = pd.DataFrame(rows)
   
    # Sauvegarder au format CSV
    df.to_csv(output_file, index=False)


queries = [
    # Amérique du Nord
    "New York", "Paris", "Moscow"
]


all_image_data = []


# Ajouter des tags pour filtrer par "outdoor"
for query in queries:
    all_image_data.extend(fetch_images_with_geo(query, tags="landscape", num_images=100))


# Sauvegarder toutes les caractéristiques dans un CSV
save_flickr_features_to_csv(all_image_data, "./test-v3/features_db.csv")