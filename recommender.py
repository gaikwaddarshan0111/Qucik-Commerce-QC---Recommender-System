# recommender.py - (Reviewing return types)
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import os

class QuickCommerceRecommender:
    def __init__(self, products_file='products.csv', interactions_file='user_interactions.csv'):
        self.products_df = pd.read_csv(products_file)
        self.interactions_df = pd.read_csv(interactions_file)
        self.tfidf_vectorizer = TfidfVectorizer(stop_words='english')
        self.product_features_matrix = None
        self.cosine_sim_matrix = None
        self.product_popularity = None

        # Add more robust checks for empty dataframes right after loading
        if self.products_df.empty:
            print("Warning: products.csv is empty or could not be loaded correctly.")
            # Consider raising an error or handling gracefully, e.g., self.is_ready = False
        if self.interactions_df.empty:
            print("Warning: user_interactions.csv is empty or could not be loaded correctly.")

        self._prepare_data()
        self._train_content_based_model()
        self._calculate_popularity()

    def _prepare_data(self):
        # Ensure 'combined_features' column is correctly handled even if description or category are missing
        self.products_df['combined_features'] = self.products_df['name'].fillna('') + ' ' + \
                                               self.products_df['category'].fillna('') + ' ' + \
                                               self.products_df['description'].fillna('')
        # Critical: if products_df is empty, this step might fail or result in an empty 'combined_features' series.
        # Ensure it's handled.
        if self.products_df.empty:
            self.product_features_matrix = None # Or an empty sparse matrix
            self.cosine_sim_matrix = None
            print("No products to train content-based model.")
            return

    def _train_content_based_model(self):
        if self.products_df.empty:
            self.product_features_matrix = None
            self.cosine_sim_matrix = None
            return # No products, no model to train

        try:
            self.product_features_matrix = self.tfidf_vectorizer.fit_transform(
                self.products_df['combined_features']
            )
            self.cosine_sim_matrix = cosine_similarity(self.product_features_matrix, self.product_features_matrix)
            print("Content-based model trained and similarity matrix computed.")
        except Exception as e:
            print(f"Error training content-based model: {e}")
            self.product_features_matrix = None
            self.cosine_sim_matrix = None # Ensure it's None on failure

    def _calculate_popularity(self):
        if self.interactions_df.empty:
            self.product_popularity = self.products_df.copy()
            self.product_popularity['purchase_count'] = 0
            self.product_popularity = self.product_popularity.sort_values(by='purchase_count', ascending=False)
            print("No interaction data, popularity set to zero for all products.")
            return

        try:
            purchase_counts = self.interactions_df[self.interactions_df['interaction_type'] == 'purchase'] \
                                                .groupby('product_id').size().reset_index(name='purchase_count')

            self.product_popularity = self.products_df.merge(purchase_counts, on='product_id', how='left')
            self.product_popularity['purchase_count'] = self.product_popularity['purchase_count'].fillna(0)
            self.product_popularity = self.product_popularity.sort_values(by='purchase_count', ascending=False)
            print("Product popularity calculated.")
        except Exception as e:
            print(f"Error calculating popularity: {e}")
            self.product_popularity = self.products_df.copy() # Fallback to products_df
            self.product_popularity['purchase_count'] = 0 # With zero counts
            self.product_popularity = self.product_popularity.sort_values(by='purchase_count', ascending=False)


    # ... (get_product_name remains the same)

    def recommend_popularity_based(self, num_recommendations=5):
        if self.product_popularity is None or self.product_popularity.empty:
            print("Popularity data not available or empty.")
            return [] # Always return an empty list
        top_popular_products = self.product_popularity.head(num_recommendations)
        return top_popular_products[['product_id', 'name', 'category', 'purchase_count']].to_dict(orient='records')


    def recommend_content_based(self, product_id, num_recommendations=5):
        if self.products_df.empty or self.cosine_sim_matrix is None:
            print("Content-based model not ready or products data empty.")
            return [] # Always return an empty list

        if product_id not in self.products_df['product_id'].values:
            print(f"Product ID {product_id} not found for content-based recommendation.")
            return [] # Product not found

        idx = self.products_df[self.products_df['product_id'] == product_id].index[0]
        sim_scores = list(enumerate(self.cosine_sim_matrix[idx]))
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

        sim_scores = sim_scores[1:num_recommendations+1] # Exclude itself

        product_indices = [i[0] for i in sim_scores]
        # Ensure recommended_products is not empty before proceeding
        if not product_indices:
            return []

        recommended_products = self.products_df.iloc[product_indices]

        recommendation_list = []
        for i, row in recommended_products.iterrows():
            rec_id = row['product_id']
            sim_score = next((score for index, score in sim_scores if index == i), None)
            recommendation_list.append({
                'product_id': rec_id,
                'name': row['name'],
                'category': row['category'],
                'similarity_score': round(sim_score, 4) if sim_score is not None else None # Handle None
            })
        return recommendation_list


    def recommend_hybrid(self, user_id=None, product_id=None, num_recommendations=5):
        recommendations = []
        recommended_ids = set()

        if product_id:
            print(f"Generating hybrid recommendations based on product_id: {product_id} ({self.get_product_name(product_id)})")
            content_recs = self.recommend_content_based(product_id, num_recommendations=num_recommendations)
            for rec in content_recs:
                if rec['product_id'] not in recommended_ids:
                    recommendations.append(rec)
                    recommended_ids.add(rec['product_id'])

            if len(recommendations) < num_recommendations:
                print("Filling with popularity-based recommendations due to insufficient content-based.")
                # Get more popularity recommendations to ensure we fill up to num_recommendations
                popularity_recs_to_consider = max(num_recommendations, 10) # Get at least 10 or num_recommendations
                popularity_recs = self.recommend_popularity_based(num_recommendations=popularity_recs_to_consider)
                for rec in popularity_recs:
                    if rec['product_id'] not in recommended_ids:
                        recommendations.append(rec)
                        recommended_ids.add(rec['product_id'])
                        if len(recommendations) >= num_recommendations:
                            break

        elif user_id:
            print(f"Generating hybrid recommendations for user_id: {user_id}. Currently falling back to popularity.")
            # Placeholder: In future, integrate collaborative filtering here.
            # For now, just return popularity-based.
            popularity_recs = self.recommend_popularity_based(num_recommendations)
            recommendations.extend(popularity_recs) # Extend instead of direct return, to ensure it's a list

        else:
            print("No specific product or user context. Recommending popular items.")
            popularity_recs = self.recommend_popularity_based(num_recommendations)
            recommendations.extend(popularity_recs) # Extend instead of direct return

        # Ensure we always return a list
        return recommendations[:num_recommendations] # Slice to ensure exact number of recommendations