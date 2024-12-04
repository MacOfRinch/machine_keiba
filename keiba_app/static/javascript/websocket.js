var socket = io.connect("http://" + document.domain + ":" + location.port, {
  transports: ['websocket'],
  reconnectionAttempts: 5,
  reconnectionDelay: 1000,
  timeout: 10000
});

socket.on('connect', () => {
  console.log('サーバーに接続できました！')
}); 

socket.on('server_message', (data) => {
  console.log(data.message);
  const nowTime = document.getElementById('last_updated');
  nowTime.textContent = `最終更新: ${data.time}`;
});

socket.on('test_job', (data) => {
  const testJob = document.getElementById('test_job');
  testJob.textContent = `テスト: ${data.time}`
});

socket.on('client_event', )
