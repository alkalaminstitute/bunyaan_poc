import React from 'react';
import Blocks from './Blocks';

function Home({blockchain}) {
    // console.log(chain)
    return (
        <div className='content'>
            <h1>Blocks in blockchain</h1>
            <p>Each card represents a block on the chain. Click on a block to see the transactions stored inside.</p>
            <Blocks blockchain={blockchain} />
        </div>
    );
}

export default Home;