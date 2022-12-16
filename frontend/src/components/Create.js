import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';

function Create({ pubKey }) {
    const [receiverAddress, setReceiverAddress] = useState("ADDRESS");
    const transactionAmount = useRef()
    const [wallets, setWallets] = useState([])
    const [isLoading, setLoading] = useState(true);

    useEffect(() => {
        axios.get('/get_wallets')
        .then(res => {
            setWallets(res.data.wallets)
            setLoading(false)
        })
  }, [])

    var request = {
        "sender": pubKey,
        "receiver": "",
        "amount": "",
        "timestamp": Date.now(),
        "signature": ""
    }

    // must also include transaction signature in request

    function handleAddTransaction(e) {
        if (receiverAddress.value === '' || transactionAmount.current.value === '' ) return
        request.receiver = receiverAddress;
        request.amount = transactionAmount.current.value
        axios.post('/add_transaction', request)
            .then(res => {
                // console.log(res);
                // console.log(res.data);
            })
        window.location.reload();
    }


    const handleChange = (e) => {
        setReceiverAddress(e.target.value)
    }

    // if (isLoading) {
    //     return <div className="Create">Loading Wallets...</div>;
    // }
    return (
        <div className='content'>
            <h3>Create a transaction</h3>
            <br />
            <form>
                <lable>FROM  </lable>
                <br />
                <input disabled type="text" id="fname" name="firstname" placeholder={pubKey}/>
                <br />
                <lable>To  </lable>
                <br /><br />
                <select className='wallet_selector' value={receiverAddress} onChange={handleChange} >
                    <option>Please Select a Wallet</option>
                    {wallets.map((wallet) => (
                        <option value={wallet}>{wallet}</option>
                    ))}
                </select>
                <br /><br />
                <p>{`You selected ${receiverAddress}`}</p>
                <br /><br />
                <lable>Amount  </lable>
                <br />
                <input ref={transactionAmount} type="text" placeholder="Amount" />
            </form>
            <br />
            <button className='create-btn' onClick={handleAddTransaction}>Add Transaction</button>
        </div>
    );
}

export default Create;