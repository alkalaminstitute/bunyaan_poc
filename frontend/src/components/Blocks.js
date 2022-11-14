import React from 'react';
import Block from './Block';
import bimage from '../assets/block.png'

function Blocks({ blockchain }) {
    // console.log(blockchain)
    const blocks = [];
    blockchain.chain.forEach(block => {
    blocks.push(
        <Block key={blockchain.chain.indexOf(block)}
            index={blockchain.chain.indexOf(block)}
            hash={block.hash}
            prevHash={block.prev_hash}
            nonce={block.nonce}
            timestamp={block.timestamp}
        />
        );
    });

    return (
        <div className='wrapper'>
            {blocks}
        </div>
    );
}

export default Blocks;