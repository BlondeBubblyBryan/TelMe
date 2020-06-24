from .models import FavoritesProducts, Cluster
from products.models import Product
from django.contrib.auth import get_user_model
from sklearn.cluster import KMeans
from scipy.sparse import dok_matrix, csr_matrix
import numpy as np

User = get_user_model()

def update_clusters():
    num_favorites = FavoritesProducts.objects.count()
    update_step = ((num_favorites/100)+1) * 5
    if num_favorites % update_step == 0: # using some magic numbers here, sorry...
        # Create a sparse matrix from user favorites
        all_user_names = map(lambda x: x.username, User.objects.only("username"))
        all_product_ids = set(map(lambda x: x.product.id, FavoritesProducts.objects.only("product")))
        num_users = len(all_user_names)
        ratings_m = dok_matrix((num_users, max(all_product_ids)+1), dtype=np.float32)
        for i in range(num_users): # each user corresponds to a row, in the order of all_user_names
            user_favorites = FavoritesProducts.objects.filter(user_name=all_user_names[i])
            for user_favorite in user_favorites:
                #if favourite, give rating of 5,
                ratings_m[i,user_favorite.product.id] = user_favorite.rating
                #else give rating of 1. 
# needs editing here

        # Perform kmeans clustering
        k = int(num_users / 10) + 2
        kmeans = KMeans(n_clusters=k)
        clustering = kmeans.fit(ratings_m.tocsr())
        
        # Update clusters
        Cluster.objects.all().delete()
        new_clusters = {i: Cluster(name=i) for i in range(k)}
        for cluster in new_clusters.values(): # clusters need to be saved before refering to users
            cluster.save()
        for i,cluster_label in enumerate(clustering.labels_):
            new_clusters[cluster_label].users.add(User.objects.get(username=all_user_names[i]))