import React from 'react';
import { Link } from 'react-router';
import axios from 'axios';
import _ from 'lodash';

import AttackListDetails from '../containers/AttackListDetails';
import NotStartedVictims from '../containers/NotStartedVictims';
import WifiScan from '../containers/Wifiscan';

import GhostPc from '../img/ghost_pc.png';

export default class NetworkOverview extends React.Component {

    constructor() {
        super();
        this.state = { attacks: [], victims: [] };
    }

    onScan = (victims) => {
        this.setState({ victims: victims });
    }

    getVictims = () => {
        axios.get('/breach/victim')
        .then(res => {
            let results = _.partition(res.data['victims'], { state: 'discovered' });
            this.setState({ victims: results[0], attacks: results[1] })
        })
        .catch(error => {
            console.log(error);
        });
    }

    componentDidMount() {
        this.getVictims();
    }

    render() {
        return(
            <div>
                <div className='container-fluid'>
                    <h1> Network Overview </h1>
                    <div className='row'>
                        <div id='mainpage' className='col-md-8 col-xs-12 col-sm-6 col-lg-8'>
                            { this.state.attacks.length > 0 ? <AttackListDetails attacks={ this.state.attacks } onReload={ this.getVictims }/> : null}
                            { this.state.victims.length > 0 ? <NotStartedVictims victims={ this.state.victims }/> : null}
                        </div>
                        <div className='button col-md-4 col-xs-6 col-lg-4'>
                            <WifiScan onUpdate={ this.onScan }/>
                            <div className='ghost'>
                                <Link to='attackconfig'>
                                    <img src={GhostPc} alt='A Ghost PC' title='Add a custom victim' className='nooutline'/>
                                    <span className='line leftpadding'>Add custom victim</span>
                                </Link>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        );
    }
}
