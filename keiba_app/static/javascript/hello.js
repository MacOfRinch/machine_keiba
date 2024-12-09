const socket = io.connect("http://" + document.domain + ":" + location.port + '/hello', {
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
    updateTable(data.data, 'race_table');
  });

  socket.on('update_main_tables', (data) => {
    console.log('新しいデータを受信しました！')
    const displayMassage = document.getElementById('message');
    displayMassage.textContent = `テスト: ${data.message}`;
    const nowTime = document.getElementById('last_updated');
    nowTime.textContent = `最終更新: ${data.time}`
    const tableIds = ['race_0', 'odds_0', 'race_1', 'odds_1', 'race_2', 'odds_2'];
    const datum = [JSON.parse(data.race_0), JSON.parse(data.odds_0), JSON.parse(data.race_1), JSON.parse(data.odds_1), JSON.parse(data.race_2), JSON.parse(data.odds_2)];
    nowTime.textContent = `最終更新: ${data.time}`;
    tableIds.forEach((tableId, index) =>{
      createTable(datum[index], tableId);
    });
  });

  function updateTable(data, tableId) {
    const table = document.getElementById(tableId)
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
  };

  function createTable(data, tableId) {
    const table = document.getElementById(tableId);
    const thead = table.querySelector('thead tr');
    const tbody = table.querySelector('tbody');

// ヘッダーの生成
    if (data.length > 0) {
      const headers = Object.keys(data[0]);
      headers.forEach(header => {
        const th = document.createElement('th');
        th.textContent = header.replace(/_/g, ''); // "_"を削除して表示を簡潔に
        thead.appendChild(th);
      });
    }

// データ行の生成
    data.forEach(row => {
      const tr = document.createElement('tr');
      Object.values(row).forEach(value => {
        const td = document.createElement('td');
        td.textContent = typeof value === 'number' ? value.toFixed(2) : value; // 数値は小数点2桁に
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
