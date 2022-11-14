import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';

function Create({ pubKey }) {
    const receiverAddress = useRef()

    var request = {
        "sender": pubKey,
        "receiver": "",
        "amount": "10",
        "timestamp": Date.now(),
        "signature": ""
    }
    
    // must also include transaction signature in request

    function handleAddTransaction(e) {
        if (receiverAddress.current.value === '') return
        request.receiver = receiverAddress.current.value;
        axios.post('/add_transaction', request)
            .then(res => {
                console.log(res);
                console.log(res.data);
            })
        window.location.reload();
    }

    console.log(pubKey)

    return (
        <div className='content'>
            <h3>Create a transaction</h3>
            <br />
            <form>
                <lable>FROM  </lable>
                <br />
                <input disabled type="text" id="fname" name="firstname" placeholder={pubKey.replace('-----BEGIN PUBLIC KEY-----','')}/>
                <br />
                <lable>To  </lable>
                <br />
                <input ref={receiverAddress} type="text" placeholder="Recepient" />
                <br />
                <lable>Amount  </lable>
                <br />
                <input ref={receiverAddress} type="text" placeholder="Amount" />
            </form>
            <br />
            <button className='create-btn' onClick={handleAddTransaction}>Add Transaction</button>
        </div>
    );
}

export default Create;