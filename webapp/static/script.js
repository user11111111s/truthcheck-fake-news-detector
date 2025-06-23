document.addEventListener('DOMContentLoaded', function() {
    const scrapeForm = document.getElementById('scrapeForm');
    const loading = document.getElementById('loading');
    const scrapeBtn = document.getElementById('scrapeBtn');
    const btnText = scrapeBtn.querySelector('.btn-text');
    const btnLoading = scrapeBtn.querySelector('.btn-loading');

    // Handle form submission
    scrapeForm.addEventListener('submit', function(e) {
        showLoading();
    });

    function showLoading() {
        loading.style.display = 'block';
        scrapeBtn.disabled = true;
        btnText.style.display = 'none';
        btnLoading.style.display = 'inline';
    }

    function hideLoading() {
        loading.style.display = 'none';
        scrapeBtn.disabled = false;
        btnText.style.display = 'inline';
        btnLoading.style.display = 'none';
    }

    // Auto-hide loading Atfer fter 30 seconds (fallback)
    setTimeout(hideLoading, 30000);
});

// Function to fill example URLs
function fillUrl(url) {
    document.getElementById('urlInput').value = url;
}

// Function to update stats dynamically
async function updateStats() {
    try {
        const response = await fetch('/api/stats');
        const stats = await response.json();
        
        document.querySelector('.stat-number').textContent = stats.total_articles;
        document.querySelectorAll('.stat-number')[1].textContent = stats.unique_sources;
        document.querySelectorAll('.stat-number')[2].textContent = stats.avg_word_count;
    } catch (error) {
        console.log('Could not update stats:', error);
    }
}

// Update stats every 30 seconds
setInterval(updateStats, 30000);