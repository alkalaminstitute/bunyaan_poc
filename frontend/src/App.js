import React, { useState, useRef, useEffect } from 'react';
import Navbar from './components/Navbar'
import './App.scss';
import axios from 'axios';
import './styles.css'
const EC = require('elliptic').ec;
const ec = new EC('secp256k1');

const LOCAL_STORAGE_BLOCKCHAIN = 'blockchain'
const LOCAL_STORAGE_KEY = 'key'


function App() {
  const [blockchain, setBlockchain] = useState([])
  const [pubKey, setPubKey] = useState([]);
  const [isLoading, setLoading] = useState(true);
  const [keyCreated, setKeyCreated] = useState(false)
  // const transactionRef = useRef()

  useEffect(() => {
      localStorage.setItem(LOCAL_STORAGE_BLOCKCHAIN, JSON.stringify(blockchain))
      localStorage.setItem(LOCAL_STORAGE_KEY, JSON.stringify(pubKey))
  }, [blockchain])

  useEffect(() => {
    const blockchain = JSON.parse(localStorage.getItem(LOCAL_STORAGE_BLOCKCHAIN))
    if (blockchain) setBlockchain(blockchain)
    // const fetchedKey = JSON.parse(localStorage.getItem(LOCAL_STORAGE_KEY))
  }, [])

  if (keyCreated) {
    // console.log(pubKey);
  }

  useEffect(() => {
    axios.get('/get_chain')
      .then(res => {
        setBlockchain(res.data)
        // console.log(res.data.chain)
        setPubKey(res.data.public_key)
        setKeyCreated(true)
        setLoading(false);
      })
  }, [])

  if (isLoading) {
      return <div className="App">Loading...</div>;
  }

  return (
    <div>
      <Navbar blockchain={blockchain} pubKey={pubKey} />
    </div>
  );
}

export default App;
