import axios from 'axios';
import React, { useState, useRef } from 'react';
import { useLocation } from "react-router-dom";

function SmartContractDetails(props) {

    const location = useLocation()
    const amount = useRef()
    const [loanRemaining, setLoanRemaining] = useState(location.state.sc.loan_remaining)
    const [loanGranted, setLoanGranted] = useState(location.state.sc.loan_granted)
    const [payed, setPayed] = useState(false)

    function handleAddPartner() {
        // console.log("HELLO")
        // console.log(location.state.sc.block_index)
        // console.log(location.state.sc.tx_index)

        var request = {
            'lender_wallet_address': location.state.pubKey,
            'contract_block_index': location.state.sc.bl_idx,
            'contract_tx_index': location.state.sc.sctx_idx,
            'loan_amount': amount.current.value
        }

        console.log(amount.current.value)

        axios.post('/add_lender_tocontract', request)
            .then(res => {
                setLoanRemaining(res.data.amount_remaining)
                setLoanGranted(res.data.loan_granted)
            }
        );
    }

    function handlePayRent() {

        var request = {
            'contract_block_index': location.state.sc.bl_idx,
            'contract_tx_index': location.state.sc.sctx_idx
        }

        axios.post('/pay_rent', request)
            .then(res => {
                setPayed(res.data.payed)
            }
        );
    }

    function BecomePartner(props) {
        return (
            <button className='card__btn' onClick={handleAddPartner}>
                Become a Partner
            </button>
        );
    }

    function PayRent(props) {
        return (
            <button className='card__btn' onClick={handlePayRent}>
                Pay Rent
            </button>
        );
    }

    let button;
    let inputHeading;
    let inputAmountTextbox;
    if (loanRemaining == 0) {
        if (location.state.sc.sender == location.state.pubKey) {
            button = <PayRent />;
            inputHeading = <p className='card__timestamp'><b>Loan Granted</b></p>;
            inputAmountTextbox = null;
        } else {
            button = null;
            inputHeading = <p className='card__timestamp'><b>Loan Granted</b></p>;
            inputAmountTextbox = null;
        }
    } else {
        if (location.state.sc.sender == location.state.pubKey) {
            inputHeading = <p className='card__timestamp'><b>Waiting for Loans</b></p>;;
            inputAmountTextbox = null;
        } else {
            inputHeading = <p className='card__timestamp'><b>Loan Amount</b></p>;
            inputAmountTextbox = <input className="small_input_box" ref={amount} type="text" id="fname" name="amount" placeholder="Amount"/>
            button = <BecomePartner />;
        }
    }

    return (
        <div className='content_scd'>
            <div className='card'>
                <div className='card__body'>
                    <p className='card__index'><b>SC Block Number</b>  {location.state.sc.block_index}</p>
                    <p className='card__hash'><b>SC Transaction Number:</b> <i>{location.state.sc.tx_index}</i></p>
                    <p className='card__prevHash'><b>Borrower:</b> <i>{location.state.sc.borrower}</i></p>
                    <p className='card__nonce'>Property: {location.state.sc.property.address}</p>
                    <p className='card__timestamp'>Seller: {location.state.sc.property.seller}</p>
                    <p className='card__timestamp'>Price: {location.state.sc.property.price}</p>
                    <p className='card__timestamp'>Downpayment: {location.state.sc.downpayment}</p>
                    <p className='card__timestamp'>Loan Granted: {loanGranted}</p>
                    <p className='card__timestamp'>Loan Remaining: {loanRemaining}</p>
                    <p className='card__timestamp'>Started: {location.state.sc.time}</p>
                    <br />
                    {inputHeading}
                    {inputAmountTextbox}
                    <br />
                    {button}
                </div>
            </div>
        </div>
    );
}

export default SmartContractDetails;