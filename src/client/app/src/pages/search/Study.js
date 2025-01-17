import React from 'react';
import SearchPanel from './SearchPanel.js';

class  DescriptionView extends React.Component{
      render(){
        return <React.Fragment>
           {this.props.obj.object.description}
        </React.Fragment>
      }
}
class  DatasetView extends React.Component{
  //send id of the study item in order to make the query for this study tag
      render(){
        return <React.Fragment>
          <SearchPanel entity_type="data" tag={"study_"+this.props.obj.object.study_id}></SearchPanel>
        </React.Fragment>
      }
}
class  TaskView extends React.Component{
      render(){
        return <React.Fragment>
           <SearchPanel entity_type="task" tag={"study_"+this.props.obj.object.study_id}></SearchPanel>
        </React.Fragment>
      }
}
class  FlowView extends React.Component{
      render(){
        return <React.Fragment>
           <SearchPanel entity_type="flow" tag={"study_"+this.props.obj.object.study_id}></SearchPanel>
        </React.Fragment>
      }
}
class  RunView extends React.Component{
      render(){
        return <React.Fragment>
           <SearchPanel entity_type="run" tag={"study_"+this.props.obj.object.study_id}></SearchPanel>
        </React.Fragment>
      }
}



export class StudyItem extends React.Component{
   constructor(props){
     super(props);
     this.object=props;
     this.state = {view: <DescriptionView obj={this.object}/>};
     this.handleClick = this.handleClick.bind(this);
   }

   handleClick(content){

     switch(content){
       case 'Description':
       this.setState({view: <DescriptionView obj={this.object}/>});
       break;
       case 'Datasets':
       this.setState({view: <DatasetView obj={this.object} />});
       break;
       case 'Tasks':
       this.setState({view: <TaskView obj={this.object} />});
       break;
       case 'Flows':
       this.setState({view: <FlowView obj={this.object}/>});
       break;
       case 'Runs':
       this.setState({view: <RunView obj={this.object}/>});
       break;
       default:
        this.setState({view: <DescriptionView obj={this.object}/>});
       break;
     }

   }

  render(){

    return <React.Fragment>
        <h1 className={"sectionTitle"}><span className={"fa fa-flask"}/>{this.props.object.name}</h1>
        <div className="dataStats">
        <div className="subtitle"></div>
            <span><span className="fa fa-cloud-upload"/>uploaded {this.props.object.date} by {this.props.object.uploader}</span>
            <span><span className="fa fa-upload"/>Visibility:{this.props.object.visibility}</span>
        </div>
        <div className="contentSection">
                <button className="button" onClick={() =>this.handleClick('Description')}> Description</button>
                <button className="button" onClick={() =>this.handleClick('Datasets')} > {this.props.object.datasets_included} Datasets</button>
                <button className="button" onClick={() =>this.handleClick('Tasks')}> {this.props.object.tasks_included} Tasks</button>
                <button className="button" onClick={() =>this.handleClick('Flows')}> {this.props.object.flows_included} Flows</button>
                <button className="button" onClick={() =>this.handleClick('Runs')}>{this.props.object.runs_included} Runs</button>
         </div>
           <div className="contentSection">
           {this.state.view}
          </div>

    </React.Fragment>
  }
}
