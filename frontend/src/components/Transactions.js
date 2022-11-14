import React from 'react';
import { Container } from 'react-bootstrap';

function Transactions({ txs }) {

  function refreshPage() {
    window.location.reload(false);
  }
  
  return (
    <div>
      <Container>
        <h3><b> Transactions </b></h3>
        <p>(Sync to get the latest transactions in the blockchain)</p>
        <br/>
        <button onClick={refreshPage}><b>SYNC</b></button>
        <table className='pending-table'>
          <thead>
            <tr>
              <th>From</th>
              <th>To</th>
              <th>Amount (Balance)</th>
              <th>Timestamp</th>
            </tr>
          </thead>
          <tbody>
            {txs.map(t =>
              <tr key={txs.indexOf(t)}>
                <td><b style={{color: '#007bff'}}>0x{t.sender}</b></td>
                <td><b style={{color: '#007bff'}}>0x{t.receiver}</b></td>
                <td><b style={{color: '#007bff'}}>{parseFloat(t.amount).toFixed(5)} </b></td>
                <td><b style={{color: '#007bff'}}>{t.time}</b></td>
              </tr>
            )}
          </tbody>
        </table>
      </Container>
    </div>
  );
}

export default Transactions;