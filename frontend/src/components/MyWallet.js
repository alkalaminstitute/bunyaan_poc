import { React, useState, useRef, useEffect } from 'react';
import axios from 'axios';
import wallet from '../assets/wallet.png'

function MyWallet({pubKey}) {

    const [walletBalance, setWalletBalance] = useState()

    var request = {
        wallet_address: pubKey,
    }

    useEffect(() => {
        axios.post('/get_wallet_balance', request)
            .then(res => {
                console.log(res.data);
                setWalletBalance(res.data.wallet_balance)
            })
    }, [])
    
    return (
        <div className='content'>
            <img className='wallet_icon' src={wallet} />
            <h4>You have {walletBalance} dinars in your wallet</h4>
        </div>
    );
}

export default MyWallet;