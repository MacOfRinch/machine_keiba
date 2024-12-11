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
    const lastTime = document.getElementById('last_updated');
    if (lastTime && lastTime.textContent.trim() === '') {
      socket.emit('request_latest_data');
    };
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

  socket.on('update_latest_data', (data) =>{
    const lastTime = document.getElementById('last_updated');
    lastTime.textContent = `最終更新: ${data.time}`

  })

  socket.on('update_table', (data) => {
    console.log('新しいテーブルデータを受信しました:');
    const nowTime = document.getElementById('last_updated');
    const noRaces = document.getElementById('no-races');
    const demoPage = document.getElementById('demo-page');
    nowTime.textContent = `最終更新: ${data.time}`;
    if (data.message === '旧') {
      noRaces.textContent = '今日はレースがありません';
      demoPage.textContent = 'このページはデモです。レースを検知すると自動で切り替わります。';
    }
    updateTable(data.data, 'race_table');
  });

  socket.on('update_main_tables', (data) => {
    const nowTime = document.getElementById('last_updated');
    const tableIds = ['race_0', 'odds_0', 'race_1', 'odds_1', 'race_2', 'odds_2'];
    const datum = tableIds.map(tableId => JSON.parse(data[tableId]));
    document.getElementById('start_0').textContent = `出走時間: ${data.start_0}`
    document.getElementById('start_1').textContent = `出走時間: ${data.start_1}`
    document.getElementById('start_2').textContent = `出走時間: ${data.start_2}`
    nowTime.textContent = `最終更新: ${data.time}`;
    tableIds.forEach((tableId, index) =>{
      updateTable(datum[index], tableId);
    });
  });

  function updateTable(data, tableId) {
    const table = document.getElementById(tableId)
    const headerRow = table.querySelector('thead tr');
    const tbody = table.querySelector('tbody');

    // ヘッダーを生成
    if (!headerRow.hasChildNodes()) {
        Object.keys(data[0]).forEach(header => {
            const th = document.createElement('th');
            th.textContent = header.replace(/_.*/g, '');
            headerRow.appendChild(th);
        });
    }

    // ボディをクリアして再生成
    tbody.innerHTML = '';
    data.forEach(row => {
        const tr = document.createElement('tr');
        Object.values(row).forEach(value => {
            const td = document.createElement('td');
            td.textContent = typeof value === 'number' ? value.toFixed(2) : value;
            tr.appendChild(td);
        });
        tbody.appendChild(tr);
    });
  };
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
