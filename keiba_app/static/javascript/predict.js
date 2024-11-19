document.getElementById('submitBtn').addEventListener('click', function() {
  const data = {
    input1: document.getElementById('input1').value,
    input2: document.getElementById('input2').value,
    input3: document.getElementById('input3').value
  };

  fetch('/api/endpoint', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(data)
  })
  .then(response => response.json())
  .then(data => {
    console.log('Success:', data);
  })
  .catch((error) => {
    console.error('Error:', error);
  });
});
