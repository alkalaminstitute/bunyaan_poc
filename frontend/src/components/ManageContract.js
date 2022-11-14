import { React, useState, useRef, useEffect } from 'react';
import axios from 'axios';

function ManageContract(props) {
    const [smartcontract, setSmartcontract] = useState()
    const blockIndex = useRef()
    const txIndex = useRef()

    function handleGetContract(e) {
        if (blockIndex.current.value === '') return
        if (txIndex.current.value === '') return

        var request = {
            block_index: blockIndex.current.value,
            tx_index: txIndex.current.value
        }
        
        axios.get('/get_smartcontract', {params: {
            block_index: blockIndex.current.value,
            tx_index: txIndex.current.value
        }})
            .then(res => {
                console.log(res.data);
                setSmartcontract(res.data)
            })
        
        document.getElementsByName('contract_form').reset()
        return false;
    }

    return (
        <div className='content'>
            <h3>Get Smart Contract</h3>
            <br />
            <form className='contract_form'>
                <lable>Block Index </lable>
                <br />
                <input ref={blockIndex} type="text" id="fname" name="block" placeholder="Block Index" />
                <br />
                <lable>Transaction Index  </lable>
                <br />
                <input ref={txIndex} type="text" placeholder="Transaction Index" />
            </form>
            <br />
            <button className='create-btn' onClick={handleGetContract}>Get Smart Contract</button>
        </div>
    );
}

export default ManageContract;