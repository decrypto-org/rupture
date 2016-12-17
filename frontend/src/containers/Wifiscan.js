import React from 'react';
import axios from 'axios';
import WifiIcon from '../img/wifiscan.png';

export default class WifiScan extends React.Component {

    constructor() {
        super();
        this.state = { 
            message: <p>Scan for victims</p> 
        };
    }

    render(){
        return(
            <div>
                <input type='image' src={WifiIcon} className='nooutline' name='wifi scan' onClick={ this.handleClick }/>
                { this.state.message }
            </div>
        );
    }
}
