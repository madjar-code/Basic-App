import { useContext } from "react";
import { Route, Redirect } from 'react-router'
import { UserContext } from "./providers/UserContext";
import PropTypes from 'prop-types'


export const NoAuthRoute = (props) => {
  const { user } = useContext(UserContext)

  return (
    <Route
      path={props.path}
      render={(data) =>
        !user ? <props.component {...data}/> : <Redirect to='/'/>
      }
    />
  )
}

NoAuthRoute.propTypes = {
  path: PropTypes.string,
}

export const ProtectedRoute = (props) => {
  const { user } = useContext(UserContext);

  return (
    <Route
      path={props.path}
      render={(data) =>
        user ? <props.component {...data} /> : <Redirect to="/login" />
      }
    />
  );
};

ProtectedRoute.propTypes = {
  path: PropTypes.string,
};