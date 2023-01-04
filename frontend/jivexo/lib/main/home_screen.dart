import 'dart:convert';
import 'dart:math';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:modal_progress_hud_nsn/modal_progress_hud_nsn.dart';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';


class HomeScreen extends StatefulWidget {
  const HomeScreen({Key? key}) : super(key: key);

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  bool showSpinner = false;
  late String loginToken;

  String getRandString(int len) {
    var random = Random.secure();
    var values = List<int>.generate(len, (i) =>  random.nextInt(255));
    return base64UrlEncode(values);
  }

  Future getLoginStatus() async{
    setState(() {
      showSpinner = true;
    });
    final prefs = await SharedPreferences.getInstance();
    final String? loginToken = prefs.getString('loginToken');
    await prefs.setString('accessToken', getRandString(18).toString());
    print(loginToken);
    if(loginToken==null){
      Navigator.pushReplacementNamed(context, '/sign-in');
    }
    setState(() {
      showSpinner = false;
    });
  }

  @override
  void initState()
  {
    super.initState();
    getLoginStatus();
  }

  @override
  Widget build(BuildContext context) {
    return const Placeholder();
  }
}
