const socket = io.connect("http://" + document.domain + ":" + location.port + '/', {
  transports: ["websocket"],
  reconnection: true,
  reconnectionAttempts: 5,
  reconnectionDelay: 1000,
  timeout: 20000
});

document.addEventListener("DOMContentLoaded", () => {
  console.log('DOMが読み込まれました。ソケット接続を開始します。');
  
  socket.on('connect', (latest_data) => {
    console.log('サーバーに接続できました！');
    const connect = document.getElementById('connect-success');
    connect.textContent = '画面は正常に更新されます';
    socket.emit('receive', {data: 'connected!'});
    const lastTime = document.getElementById('last_updated');
    if (lastTime && lastTime.textContent.trim() === '') {
      socket.emit('request_latest_data');
    };
    lastTime.textContent = `最終更新: ${latest_data.time}`;
    socket.emit('request_table_data');
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

  socket.on('update_table', (data) => {
    console.log('新しいテーブルデータを受信しました:');
    const nowTime = document.getElementById('last_updated');
    nowTime.textContent = `最終更新: ${data.time}`;
    updateTable(data.data);
});

  function updateTable(data) {
    const table = document.getElementById('race_table');
    const headerRow = table.querySelector('thead tr');
    const tbody = table.querySelector('tbody');

    // ヘッダーを生成
    if (!headerRow.hasChildNodes()) {
        Object.keys(data[0]).forEach(key => {
            const th = document.createElement('th');
            th.textContent = key;
            headerRow.appendChild(th);
        });
    }

    // ボディをクリアして再生成
    tbody.innerHTML = '';
    data.forEach(row => {
        const tr = document.createElement('tr');
        Object.values(row).forEach(value => {
            const td = document.createElement('td');
            td.textContent = value;
            tr.appendChild(td);
        });
        tbody.appendChild(tr);
    });
  }
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
