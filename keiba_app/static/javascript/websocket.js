const socket = io.connect("http://" + document.domain + ":" + location.port + '/', {
  transports: ["websocket"],
  reconnection: true,
  reconnectionAttempts: 5,
  reconnectionDelay: 1000,
  timeout: 20000
});

document.addEventListener("DOMContentLoaded", () => {
  console.log('DOMが読み込まれました。ソケット接続を開始します。');
  
  socket.on('connect', () => {
    console.log('サーバーに接続できました！');
    const connect = document.getElementById('connect-success');
    connect.textContent = '画面は正常に更新されます';
    socket.emit('receive', {data: 'connected!'});
    socket.emit('request_latest_data');
  });

  socket.on('response', (data) =>{
    console.log(data.message);
  });

  socket.on('connect_error', (error) => {
    console.error('接続エラー:', error);
    const connect = document.getElementById('connect-success');
    connect.textContent = '画面が更新されない状態になっています。再読み込みしてください。';
  });

  socket.on('disconnect', () => {
    console.log('サーバーとの接続が切れました');
    const connect = document.getElementById('connect-success');
    connect.textContent = '画面が更新されない状態になっています。再読み込みしてください。';
  });

  socket.on('test_event', (data) => {
    console.log('データを受信しました:', data);
    if (data) {
        console.log(`受信したデータ: メッセージ=${data.message}, 時間=${data.time}`);
    } else {
        console.error('データがnullまたはundefinedです');
    }
    const nowTime = document.getElementById('last_updated');
    if (nowTime) {
        nowTime.textContent = `最終更新: ${data.time}`;
    } else {
        console.log('last_updated要素が見つかりません');
    }
  });
});

window.addEventListener("beforeunload", () => {
  if (socket.connected) {
    socket.disconnect();
  }
});

// socket.on('server_event', (data) => {
//   const raceData = document.getElementById(data.race_id);
//   const nowTime = document.getElementById('last_updated');
//   nowTime.textContent = `最終更新: ${data.time}`;
// });

// socket.on('test_job', (data) => {
//   const testJob = document.getElementById('test_job');
//   testJob.textContent = `テスト: ${data.time}`;
// });
