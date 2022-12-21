import React, { Component, useState, useRef, useEffect } from 'react';
import Transactions from './Transactions';
import axios from 'axios';

const LOCAL_STORAGE_KEY = 'pending'

function Pending({ pending, pubKey }) {
    console.log(pubKey)
    const [pendingTransactions, setpendingTransactions] = useState([])
    // const transactionRef = useRef()
    
    useEffect(() => {
        const pendingTxs = JSON.parse(localStorage.getItem(LOCAL_STORAGE_KEY))
        if (pendingTxs) setpendingTransactions(pendingTxs)
    }, [])

    useEffect(() => {
        localStorage.setItem(LOCAL_STORAGE_KEY, JSON.stringify(pendingTransactions))
    }, [pendingTransactions])

    const request = {
        "miner_address": pubKey
    }

    function mineTransactions(e) {
        axios.post('/mine_block', request)
            .then(res => {
                console.log(res);
                console.log(res.data);
            })
        window.location.reload();
    }

    return (
        <div className='content'>
            <Transactions txs={pending} />
            <button className='mine-btn' onClick={mineTransactions}>Mine Transaction</button>
        </div>
    );
}

export default Pending;