import React, { useState, useEffect } from 'react';
import axios from 'axios';
import Smartcontract from './Smartcontract';

function Invest({pubKey}) {
    const [musharakahScs, setMusharakahScs] = useState()
    const [isLoading, setLoading] = useState(true);

    useEffect(() => {
        axios.get('/get_musharak_scs')
        .then(res => {
            setMusharakahScs(res.data.musharaka_scs)
            setLoading(false);
            console.log(res.data.number)
        })
    }, [])


    const scs = [];

    if (isLoading) {
        return <div className="App">Loading...</div>;
    } 

    musharakahScs.forEach(sc => {
        scs.push(<Smartcontract pubKey={pubKey} sc={sc}/>);
    });

    return (
        <div className='wrapper'>
            {scs}
        </div>
    );
}

export default Invest;