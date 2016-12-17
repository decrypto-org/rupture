import React from 'react';
import axios from 'axios';
import WifiIcon from '../img/wifiscan.png';

export default class WifiScan extends React.Component {

    constructor() {
        super();
        this.state = { 
            scanning: false
        };
    }

    handleClick = () => {
        this.setState({ scanning: true });

        axios.get('/breach/victim/notstarted')
        .then(res => {
            let victims = res.data['new_victims'];
            this.props.onUpdate(victims);
            this.setState({ scanning: false })
        })
        .catch(error => {
            console.log(error);
            this.setState({ scanning: false })
        });
    } 
                
    render(){
        return(
            <div>
                <img type='image' src={WifiIcon} className='nooutline' alt='wifi button'
                    name='wifi scan' onClick={ this.handleClick }/>
                { this.state.scanning ? <p>Scanning...</p> : <p>Scan for victims</p> }
            </div>
        );
    }
}
