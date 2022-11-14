import React from 'react';
import scimage from '../assets/smartcontract.png'
import { useNavigate } from 'react-router-dom';

function Smartcontract({ pubKey, sc }) {
    const navigate = useNavigate()

    function handleDetailsPage() {
        navigate('/invest/scdetails', {
            state: {
                sc: sc,
                pubKey: pubKey
            }
        });
    }
    
    return (
        <div className='card'>
            <div className='card__body'>
                <img className='card__image' src={scimage} />
                <p className='card__index'><b>SC Block Number</b>  {sc.bl_idx}</p>
                <p className='card__hash'><b>SC Transaction Number:</b> <i>{sc.sctx_idx}</i></p>
                <p className='card__prevHash'><b>Borrower:</b> <i>{sc.sender}</i></p>
                <p className='card__nonce'>Property: {sc.property.address}</p>
                <p className='card__timestamp'>Seller: {sc.property.seller}</p>
                <p className='card__timestamp'>Price: {sc.property.price}</p>
                <p className='card__timestamp'>Downpayment: {sc.downpayment}</p>
                <p className='card__timestamp'>Loan Granted: {sc.loan_granted}</p>
                <p className='card__timestamp'>Loan Remaining: {sc.loan_remaining}</p>
                <p className='card__timestamp'>Started: {sc.time}</p>
                <button disabled={sc.pending} className='card__btn' onClick={handleDetailsPage}>SC Details</button>
            </div>
        </div>
    );
}

export default Smartcontract;