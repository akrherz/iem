document.addEventListener('DOMContentLoaded', () => {
    // Handle map station selection
    const addMapStationsBtn = document.getElementById('addmapstations');
    if (addMapStationsBtn) {
        addMapStationsBtn.addEventListener('click', () => {
            const stationsOut = document.getElementById('stations_out');
            if (stationsOut) {
                stationsOut.setAttribute('name', 's[]');
            }
        });
    }

    // Handle date format conversion for form submission
    const dateForm = document.querySelector('form[name="dates"]');
    if (dateForm) {
        dateForm.addEventListener('submit', () =>{
            const sdateInput = document.getElementById('sdate');
            const edateInput = document.getElementById('edate');

            if (sdateInput && sdateInput instanceof HTMLInputElement && sdateInput.value) {
                // Convert from YYYY-MM-DD to MM/DD/YYYY for PHP
                // Parse the date string directly to avoid timezone issues
                const dateParts = sdateInput.value.split('-');
                const year = dateParts[0];
                const month = dateParts[1];
                const day = dateParts[2];
                const sdateFormatted = `${month}/${day}/${year}`;

                // Create hidden input for PHP format
                const hiddenSdate = document.createElement('input');
                hiddenSdate.type = 'hidden';
                hiddenSdate.name = 'sdate';
                hiddenSdate.value = sdateFormatted;
                dateForm.appendChild(hiddenSdate);

                // Remove name from visible input to avoid conflict
                sdateInput.removeAttribute('name');
            }

            if (edateInput && edateInput instanceof HTMLInputElement && edateInput.value) {
                // Convert from YYYY-MM-DD to MM/DD/YYYY for PHP
                // Parse the date string directly to avoid timezone issues
                const dateParts = edateInput.value.split('-');
                const year = dateParts[0];
                const month = dateParts[1];
                const day = dateParts[2];
                const edateFormatted = `${month}/${day}/${year}`;

                // Create hidden input for PHP format
                const hiddenEdate = document.createElement('input');
                hiddenEdate.type = 'hidden';
                hiddenEdate.name = 'edate';
                hiddenEdate.value = edateFormatted;
                dateForm.appendChild(hiddenEdate);

                // Remove name from visible input to avoid conflict
                edateInput.removeAttribute('name');
            }
        });
    }
});
