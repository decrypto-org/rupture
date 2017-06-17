import React from 'react'; 

export default class VictimIP extends React.Component {
		
    constructor() {
        super();
        this.state = { sourceip: '' };
    }
    
    handleIP = () => {
        this.setState({ sourceip: this.refs.victimip.value });
        this.props.onUpdate(this.refs.victimip.value);
    }  

    render() {
        return(
            <div>
                <label htmlFor='ip' className='col-md-4 col-sm-6 attackpagefields'>IP:&nbsp;</label>
                <div className='col-md-6 progressmargin'>
                    <input type='text' className='form-control' placeholder='192.168.1.2' ref='victimip' 
                        value={ this.props.sourceip }
                        onChange={ this.handleIP }/>
                </div>
            </div>
        );
    }
}
