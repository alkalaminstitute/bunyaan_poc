import { NavLink, Routes, Route, useLocation } from "react-router-dom"
import React from 'react';
import Home from './Home';
import Pending from "./Pending";
import Create from "./Create";
import BeginSmartContract from "./BeginSmartContract";
import ManageContract from "./ManageContract";
import Invest from "./Invest";
import SmartContractDetails from "./SmartContractDetails"
import MyWallet from "./MyWallet";


function Navbar({ blockchain, pubKey }) {
    // var isActive = useLocation() === window.location.pathname;
    // console.log(useLocation().pathname)
    // console.log(window.location.pathname)
    // var className = isActive ? 'active' : '';
    return (
        <>
            <nav className='nav'>
                <a href="/" className='site-title'>bunyaan</a>
                <ul>
                    <li>
                        <NavLink to="/mywallet" activeClassName="active">
                            My Wallet
                        </NavLink>
                    </li>
                    <li>
                        <NavLink to="/pending" activeClassName="active">
                            Pending Transactions
                        </NavLink>
                    </li>
                    <li>
                        <NavLink to="/create" activeClassName="active">
                            Create Transaction
                        </NavLink>
                    </li>
                    <li>
                        <NavLink to="/beginsmartcontract" activeClassName="active">
                            Start Smart Contract
                        </NavLink>
                    </li>
                    {/* <li>
                        <NavLink to="/getsmartcontract" activeClassName="active">
                            Get Smart Contract
                        </NavLink>
                    </li> */}
                    <li>
                        <NavLink to="/invest" activeClassName="active">
                            Musharakh Investments
                        </NavLink>
                    </li>
                </ul>
            </nav>
            <Routes>
                <Route path="/" element={ <Home blockchain={blockchain}/> } />
                <Route path="/pending" element={ <Pending pending={blockchain.pending_transactions} pubKey={pubKey} /> } />
                <Route path="/create" element={<Create pubKey={pubKey} />} />
                <Route path="/beginsmartcontract" element={<BeginSmartContract pubKey={pubKey} />} />
                {/* <Route path="/getsmartcontract" element={<ManageContract pubKey={pubKey} />} /> */}
                <Route path="/invest" element={<Invest pubKey={pubKey} />} />
                <Route path="/invest/scdetails" element={<SmartContractDetails pubKey={pubKey} />} />
                <Route path="/mywallet" element={<MyWallet pubKey={pubKey} />} />
            </Routes>
            {/* <Home chain={chain.chain} /> */}
        </>
    );
}

export default Navbar;