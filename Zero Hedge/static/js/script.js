function search() {
    var product = document.getElementById('product').value;
        if (!product.trim()) {
        alert('Please fill in the product field.');
        return;
    }

    document.getElementById('file-data-content').innerText += '\nScraping...'
    fetch('/search', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            product: product,
        })
    })
    .then(response => response.json())
    .then(data => {
        alert(JSON.stringify(data))
    })
    .catch((error) => {
        console.error('Error:', error);
    });
}

document.getElementById('search-button').addEventListener('click', search);

document.addEventListener("DOMContentLoaded", function () {
    document.getElementById("terminate-subprocess").addEventListener("click", function () {
        fetch("/terminate-subprocess", {
            method: "POST"
        })
        .then(response => response.json())
        .then(data => {
            console.log(data.message);
            alert(JSON.stringify(data))
        })
        .catch(error => {
            console.error("Error:", error);
        });
    });
});

window.addEventListener("beforeunload", function(e) {
    var xhr = new XMLHttpRequest();
    xhr.open("POST", "/terminate-subprocess", true);
    xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
    xhr.send();
});

function renderTableData(item) {
    var row = document.createElement('tr');
    row.innerHTML = `
        <td>${item.Title || ''}</td>
        <td>${item.authorName || ''}</td>
        <td>${item.dateTime || ''}</td>
        <td>${item.category || ''}</td>
        <td>${item.type || ''}</td>
        <td>${item.relevance || ''}</td>
        <td>${item.url || ''}</td>
        <td>${item.comments || ''}</td>
        <td>${item.views || ''}</td>
        <td>${Array.isArray(item.imageUrls) ? item.imageUrls.join(', ') : ''}</td>
        <td>${Array.isArray(item.references) ? item.references.join(', ') : ''}</td>
        <td>${item.content || ''}</td>
    `;
    document.getElementById('listing-table-body').appendChild(row);
}


function fetchTableData() {
    fetch('/data')
        .then(response => response.json())
        .then(data => {
            renderTableData(data);
        })
        .catch((error) => {
            console.error('Error:', error);
        });
}
setInterval(fetchTableData, 3500);
