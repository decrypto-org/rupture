import React from 'react'
import ReactDOM from 'react-dom'
import { Router, Route, IndexRoute, browserHistory } from 'react-router';

import Layout from './pages/Layout';
import NetworkOverview from './pages/NetworkOverview';
import AttackConfig from './pages/AttackConfig';
import AttackInspection from './pages/AttackInspection';
import './style.css'
import '../bower_components/bootstrap/dist/css/bootstrap.min.css'

const app = document.getElementById('app');

ReactDOM.render(
    <Router history={ browserHistory }>
        <Route path='/' component={ Layout }>
            <IndexRoute component={ NetworkOverview }></IndexRoute>
            <Route path='attackConfig(/:id)' name='attackconfig' component={ AttackConfig }></Route>
            <Route path='attackInspection(/:victim_id)' name='attackinspect' component={ AttackInspection }></Route>
        </Route>
    </Router>,
app);
