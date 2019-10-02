import FrontEnd, Dashboard#mysql

if __name__ == '__main__':
    #ControllerFrontend = FrontEnd.initialize_frontend()
    #ControllerFrontend.run_server(debug=True)
    TankControllerFrontEnd = Dashboard.InitializeFrontend()
    TankControllerFrontEnd.run_server(debug=True, port=8050)