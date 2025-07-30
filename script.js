// static/script.js

async function getRecommendations() {
    // Check these IDs carefully against index.html
    const productId = document.getElementById('product_id').value;
    const numRecs = document.getElementById('num_recommendations').value;
    const recommendationsList = document.getElementById('recommendations-list');
    const errorMessageDiv = document.getElementById('error-message');


    // Clear previous recommendations and error message
    recommendationsList.innerHTML = '<p>Loading recommendations...</p>';
    errorMessageDiv.style.display = 'none';
    errorMessageDiv.textContent = '';

    let url = `/recommendations?num_recommendations=${numRecs}`;
    if(productId){
        url +=`&product_id=${productId}`;
    }


    try {
        const response = await fetch(url);
        const data = await response.json();

        if (!response.ok) {
            // Handle HTTP errors (e.g., 400, 500)
            throw new Error(data.error || `HTTP error! Status: ${response.status}`);
        }

        recommendationsList.innerHTML = ''; // Clear previous recommendations
        if (data.message) { // Check for "No recommendations available" message
            recommendationsList.innerHTML = `<p>${data.message}</p>`;
        } else if (data.length === 0) {
            recommendationsList.innerHTML = '<p>No recommendations found for your request.</p>';
        } else {
            data.forEach(rec => {
                const card = document.createElement('div');
                card.className = 'recommendation-card';
                card.innerHTML = `
                    <h3>${rec.name}</h3>
                    <p><strong>ID:</strong> ${rec.product_id}</p>
                    <p><strong>Category:</strong> ${rec.category}</p>
                    ${rec.purchase_count !== undefined ? `<p><strong>Purchases:</strong> ${rec.purchase_count}</p>` : ''}
                    ${rec.similarity_score !== undefined ? `<p><strong>Similarity:</strong> ${rec.similarity_score}</p>` : ''}
                `;
                recommendationsList.appendChild(card);
            });
        }
    } catch (error) {
        console.error('Error fetching recommendations:', error);
        recommendationsList.innerHTML = ''; // Clear loading message
        errorMessageDiv.textContent = `Error: ${error.message}`;
        errorMessageDiv.style.display = 'block';
    }
}

function clearResults() {
    document.getElementById('recommendations-list').innerHTML = '<p>Enter a Product ID or click "Get Recommendations" for general popular items.</p>';
    document.getElementById('product_id').value = ''; // Clear product ID input
    document.getElementById('error-message').style.display = 'none';
    document.getElementById('error-message').textContent = '';
}

// Optional: Fetch recommendations on page load (e.g., popular items)
// document.addEventListener('DOMContentLoaded', () => {
//     getRecommendations();
// });
    



