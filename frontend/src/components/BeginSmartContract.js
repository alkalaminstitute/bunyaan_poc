import { React, useState, useRef, useEffect } from 'react';
import axios from 'axios';

function BeginSmartContract({ pubKey }) {
    
    const [contractTxIndex, setTxIndex] = useState("")
    const [contractBlockIndex, setBlockIndex] = useState("");
    const address = useRef()
    const price = useRef()
    const downpayment = useRef()
    const seller = useRef()

    function handleBeginContract(e) {
        if (address.current.value === '') return
        if (price.current.value === '') return
        if (downpayment.current.value === '') return
        if (seller.current.value === '') return

        var request = {
            wallet_address: pubKey,
            address: address.current.value,
            price: price.current.value,
            downpayment: downpayment.current.value,
            seller: seller.current.value
        }
        
        axios.post('/add_smartcontract', request)
            .then(res => {
                console.log(res.data);
                setTxIndex(res.data.contract_tx_index)
                setBlockIndex(res.data.contract_block_index)
            })
        document.getElementById("contract_form").reset();
    }

    return (
        <div className='content'>
            <h3>Begin Smart Contract</h3>
            <br />
            <form id='contract_form'>
                <lable>Property Address  </lable>
                <br />
                <input ref={address} type="text" id="fname" name="firstname" placeholder="Address" />
                <br />
                <lable>Price  </lable>
                <br />
                <input ref={price} type="text" placeholder="Price" />
                <br />
                <lable>Downpayment  </lable>
                <br />
                <input ref={downpayment} type="text" placeholder="Downpayment" />
                <br />
                <lable>Seller  </lable>
                <br />
                <input ref={seller} type="text" placeholder="Seller" />
            </form>
            <br />
            <button className='create-btn' onClick={handleBeginContract}>Begin Smart Contract</button>
        </div>
    );
}

export default BeginSmartContract;