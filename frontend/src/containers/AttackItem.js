import React from 'react';
import { Link } from 'react-router';
import DeleteNotification  from './DeleteNotification';
import axios from 'axios';
import GreenPC from '../img/green_pc.png'
import PlayPC from '../img/yellow_play_pc.png'
import PausePC from '../img/yellow_pause_pc.png'

export default class AttackItem extends React.Component {
    constructor() {
        super();
        this.state = { showNotification: false, attackState: '' };
    }

    deleteVictim = (deleted) => {
        axios.patch('/breach/victim/' + this.props.attack.victim_id + '/', {
            victim_id: this.props.attack.victim_id,
            deleted: deleted
        })
        .then(res => {
            console.log(res);
        })
        .catch(error => {
            console.log(error);
        });
    }

    handleVictimState = () => {
        let desiredState = '';
        if (this.state.attackState === 'running') {
            this.setState({attackState: 'paused'});
            desiredState = 'paused'
        }
        else if (this.state.attackState === 'paused') {
            this.setState({attackState: 'running'});
            desiredState = 'running'
        }
        axios.patch('/breach/victim/' + this.props.attack.victim_id + '/', {
            victim_id: this.props.attack.id,
            state: desiredState
        })
        .then(res => {
            console.log(res);
        })
        .catch(error => {
            console.log(error);
        });
    }

    handleDelete = () => {
        this.setState({ showNotification: true });
        this.deleteVictim(true);
        setTimeout(
            () => {
                this.setState({ showNotification: false });
                this.props.onReload();
            },
            10000
        );
    }

    onUndo = ()  => {
        this.setState({ showNotification: false });
        this.deleteVictim(false);
    }

    onVerify = () => {
        this.setState({ showNotification: false });
        this.props.onReload();
    }

    checkTime = (i) => {
        if (i < 10) {i = "0" + i};  // add zero in front of numbers < 10
        return i;
    }

    runningTime = () => {
        let start_time = new Date(this.props.attack.start_time * 1000);
        let now = new Date();
        let time = Math.abs(now - start_time) / 1000 ;
        let hours = Math.floor(time/3600);
        hours = this.checkTime(hours);
        let minutes = Math.floor((time - hours*3600) / 60);
        minutes = this.checkTime(minutes);
        let seconds = parseInt(time - hours*3600 - minutes*60, 10);
        seconds = this.checkTime(seconds);
        this.setState({ hours: hours, minutes: minutes, seconds: seconds})
    }

    componentDidMount = () => {
        let interval = window.setInterval(() => {
            this.runningTime();
        }, 1000);
        this.setState({ 
            interval: interval,
            attackState: this.props.attack.state
        });
        this.runningTime();
    }

    componentWillUnmount = () => {
        window.clearInterval(this.state.interval);
    }

    render() {
        let attack = this.props.attack;
        let attackState = this.state.attackState;
        let progressClass, imgsrc;
        let progressStyle = {
            width: attack.percentage
        }
        
        switch(attackState) {
            case 'completed':
                imgsrc = GreenPC;
                progressClass = 'progress-bar progress-bar-success progress-bar-striped';
                break;
            case 'running':
                imgsrc = PausePC;
                progressClass = 'progress-bar progress-bar-info progress-bar-striped active';
                break;
            case 'paused':
                imgsrc = PlayPC;
                progressClass = 'progress-bar progress-bar-info progress-bar-striped active';
                break;
            default:        
                return false
        }
        return(
            <li key={ attack.victim_id } className={ attackState } >
                <div className='btn zeropad'>
                    <button type='button' className='close nooutline' onClick={ () => this.handleDelete() }>
                        &times;
                    </button>
                    { this.state.showNotification ? <DeleteNotification onUndo={ () => this.onUndo(attack.victim_id) }
                        onClose={ this.onVerify } /> : null }
                    <input type='image' src={ imgsrc } className='pull-left nooutline' name='running attack'
                        onClick={ () => this.handleVictimState(this.state.attackState) }/>
                </div>
                <ul>
                    <li key='1' className='state'> { attackState } </li>
                    <li key='2' > { attack.sourceip } </li>
                    <li key='3'> { attack.target_name } </li>
                    <li key='4'>
                        <div className='progress progressmargin'>
                            <div className={ progressClass } style={ progressStyle }>
                                { attack.percentage }
                            </div>
                        </div>
                    </li>
                    <li key='5'> { this.state.hours }:{ this.state.minutes }:{ this.state.seconds } </li>
                    <li key='6'>
                        <Link to={{ pathname: '/attackInspection/' + attack.victim_id + '/' }}>
                            more details
                        </Link>
                    </li>
                </ul>
            </li>
        );
    }
}

