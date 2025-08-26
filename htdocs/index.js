// Vanilla JavaScript - no jQuery
function onFeatureData(data) {
    const goodVotes = document.getElementById("feature_good_votes");
    const badVotes = document.getElementById("feature_bad_votes");
    const abstainVotes = document.getElementById("feature_abstain_votes");
    const featureMsg = document.getElementById("feature_msg");
    const featureBtns = document.querySelectorAll("button.feature_btn");
    
    if (goodVotes) goodVotes.textContent = data.good;
    if (badVotes) badVotes.textContent = data.bad;
    if (abstainVotes) abstainVotes.textContent = data.abstain;
    
    if (!data.can_vote) {
        if (featureMsg) {
            featureMsg.innerHTML = '<i class="bi bi-check-lg" aria-hidden="true"></i> Thanks for voting!';
        }
        featureBtns.forEach(btn => {
            btn.disabled = true;
        });
    }
}

// Fetch data using modern fetch API
async function fetchFeatureData(url) {
    const response = await fetch(url);
    if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
    }
    const data = await response.json();
    onFeatureData(data);
}

// Add event listeners when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    // Add click handlers to feature buttons
    const featureBtns = document.querySelectorAll("button.feature_btn");
    featureBtns.forEach(btn => {
        btn.addEventListener('click', (event) => {
            const voting = event.target.dataset.voting;
            if (voting) {
                fetchFeatureData(`/onsite/features/vote/${voting}.json`);
            }
        });
    });
    
    // Load initial vote data
    fetchFeatureData("/onsite/features/vote.json");
});