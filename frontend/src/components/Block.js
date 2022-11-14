import React from 'react';
import bimage from '../assets/block.png'
import TransactionList from './TransactionList';

function Block({ index, hash, prevHash, nonce, timestamp }) {
    // console.log(hash)
    return (
        <div className='card'>
            <div className='card__body'>
                <img className='card__image' src={bimage} />
                <h3 className='card__index'>Block Number {index}</h3>
                <p className='card__hash'><b>Hash:</b> <i>{hash}</i></p>
                <p className='card__prevHash'><b>Previous Hash:</b> <i>{prevHash}</i></p>
                <p className='card__nonce'>Nonce: {nonce}</p>
                <p className='card__timestamp'>Timestamp: {timestamp}</p>
                <button className='card__btn'>Block Details</button>
            </div>
        </div>
    );
}

export default Block;